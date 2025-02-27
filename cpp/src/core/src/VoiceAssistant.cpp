#include "VoiceAssistant.hpp"
#include "Logger.hpp"
#include "Config.hpp"
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>

VoiceAssistant::VoiceAssistant(QObject* parent)
    : QObject(parent)
    , player_(std::make_unique<QMediaPlayer>())
    , audioOutput_(std::make_unique<QAudioOutput>())
    , volume_(1.0f)
    , speed_(1.0f)
    , enabled_(true)
{
    player_->setAudioOutput(audioOutput_.get());
    
    connect(player_.get(), &QMediaPlayer::playbackStateChanged,
            this, &VoiceAssistant::onPlaybackStateChanged);
    connect(player_.get(), &QMediaPlayer::mediaStatusChanged,
            this, &VoiceAssistant::onMediaStatusChanged);
    connect(player_.get(), &QMediaPlayer::errorOccurred,
            this, &VoiceAssistant::onErrorOccurred);
            
    // Load default voice samples
    loadVoiceSamples(Config::instance().getResourcePath() + "/voices");
}

VoiceAssistant& VoiceAssistant::instance()
{
    static VoiceAssistant instance;
    return instance;
}

void VoiceAssistant::speak(const QString& messageId, const QVariantMap& params)
{
    if (!enabled_) {
        return;
    }

    QueuedMessage message{messageId, params, false};
    messageQueue_.enqueue(message);
    
    if (player_->playbackState() != QMediaPlayer::PlayingState) {
        processNextMessage();
    }
}

void VoiceAssistant::stopSpeaking()
{
    messageQueue_.clear();
    player_->stop();
}

void VoiceAssistant::pauseSpeaking()
{
    if (player_->playbackState() == QMediaPlayer::PlayingState) {
        player_->pause();
    }
}

void VoiceAssistant::resumeSpeaking()
{
    if (player_->playbackState() == QMediaPlayer::PausedState) {
        player_->play();
    }
}

void VoiceAssistant::setVolume(float volume)
{
    volume_ = qBound(0.0f, volume, 1.0f);
    audioOutput_->setVolume(volume_);
    emit volumeChanged(volume_);
}

void VoiceAssistant::setSpeed(float speed)
{
    speed_ = qBound(0.5f, speed, 2.0f);
    player_->setPlaybackRate(speed_);
    emit speedChanged(speed_);
}

void VoiceAssistant::setEnabled(bool enabled)
{
    if (enabled_ != enabled) {
        enabled_ = enabled;
        emit enabledChanged(enabled_);
        
        if (!enabled_) {
            stopSpeaking();
        }
    }
}

void VoiceAssistant::setContext(const QString& context)
{
    if (currentContext_ != context) {
        currentContext_ = context;
        emit contextChanged(context);
        
        // Play contextual hints if available
        if (contextHints_.contains(context)) {
            for (const QString& hintId : contextHints_[context]) {
                speak(hintId);
            }
        }
    }
}

void VoiceAssistant::addContextualHint(const QString& context, const QString& messageId)
{
    if (!contextHints_[context].contains(messageId)) {
        contextHints_[context].append(messageId);
    }
}

void VoiceAssistant::removeContextualHint(const QString& context, const QString& messageId)
{
    if (contextHints_.contains(context)) {
        contextHints_[context].removeAll(messageId);
    }
}

bool VoiceAssistant::loadVoiceSamples(const QString& voicePath)
{
    QDir voiceDir(voicePath);
    if (!voiceDir.exists()) {
        Logger::instance().error("Voice samples directory does not exist: " + voicePath);
        return false;
    }
    
    // Load voice metadata
    QFile metadataFile(voiceDir.filePath("metadata.json"));
    if (!metadataFile.open(QIODevice::ReadOnly)) {
        Logger::instance().error("Failed to open voice metadata file");
        return false;
    }
    
    QJsonDocument metadata = QJsonDocument::fromJson(metadataFile.readAll());
    metadataFile.close();
    
    if (!metadata.isObject()) {
        Logger::instance().error("Invalid voice metadata format");
        return false;
    }
    
    // Clear existing samples
    voiceSamples_.clear();
    
    // Load each voice sample
    QJsonObject root = metadata.object();
    QJsonArray samples = root["samples"].toArray();
    
    for (const QJsonValue& sample : samples) {
        QJsonObject sampleObj = sample.toObject();
        QString sampleId = sampleObj["id"].toString();
        QString samplePath = voiceDir.filePath(sampleObj["file"].toString());
        
        VoiceSample voiceSample;
        voiceSample.path = samplePath;
        voiceSample.text = sampleObj["text"].toString();
        voiceSample.duration = sampleObj["duration"].toDouble();
        voiceSample.metadata = sampleObj["metadata"].toObject().toVariantMap();
        
        voiceSamples_[sampleId] = voiceSample;
    }
    
    Logger::instance().info(QString("Loaded %1 voice samples").arg(voiceSamples_.size()));
    return true;
}

bool VoiceAssistant::setActiveVoice(const QString& voiceId)
{
    if (currentVoiceId_ != voiceId) {
        currentVoiceId_ = voiceId;
        emit voiceChanged(voiceId);
        return true;
    }
    return false;
}

void VoiceAssistant::processNextMessage()
{
    if (messageQueue_.isEmpty() || !enabled_) {
        return;
    }
    
    QueuedMessage message = messageQueue_.dequeue();
    QString sampleId = findBestMatch(message.messageId, message.params);
    
    if (!voiceSamples_.contains(sampleId)) {
        Logger::instance().warning("No voice sample found for message: " + message.messageId);
        processNextMessage();
        return;
    }
    
    const VoiceSample& sample = voiceSamples_[sampleId];
    player_->setSource(QUrl::fromLocalFile(sample.path));
    player_->play();
    
    emit speakingStarted(message.messageId);
}

QString VoiceAssistant::findBestMatch(const QString& messageId, const QVariantMap& params)
{
    // Simple direct mapping for now
    // TODO: Implement more sophisticated matching based on context and parameters
    return messageId;
}

void VoiceAssistant::onPlaybackStateChanged(QMediaPlayer::PlaybackState state)
{
    switch (state) {
        case QMediaPlayer::StoppedState:
            if (!messageQueue_.isEmpty()) {
                processNextMessage();
            }
            break;
        default:
            break;
    }
}

void VoiceAssistant::onMediaStatusChanged(QMediaPlayer::MediaStatus status)
{
    switch (status) {
        case QMediaPlayer::EndOfMedia:
            emit speakingFinished(messageQueue_.isEmpty() ? QString() : messageQueue_.head().messageId);
            break;
        default:
            break;
    }
}

void VoiceAssistant::onErrorOccurred(QMediaPlayer::Error error, const QString& errorString)
{
    Logger::instance().error("Voice playback error: " + errorString);
    emit errorOccurred(errorString);
    
    // Skip to next message on error
    processNextMessage();
}
