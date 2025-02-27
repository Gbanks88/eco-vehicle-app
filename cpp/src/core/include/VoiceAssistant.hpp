#pragma once

#include <QObject>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QString>
#include <QMap>
#include <QQueue>
#include <memory>

class VoiceAssistant : public QObject {
    Q_OBJECT

public:
    static VoiceAssistant& instance();

    // Voice playback control
    void speak(const QString& messageId, const QVariantMap& params = QVariantMap());
    void stopSpeaking();
    void pauseSpeaking();
    void resumeSpeaking();
    
    // Voice configuration
    void setVolume(float volume);
    void setSpeed(float speed);
    void setEnabled(bool enabled);
    
    // Context-aware narration
    void setContext(const QString& context);
    void addContextualHint(const QString& context, const QString& messageId);
    void removeContextualHint(const QString& context, const QString& messageId);

    // Load voice samples
    bool loadVoiceSamples(const QString& voicePath);
    bool setActiveVoice(const QString& voiceId);

signals:
    void speakingStarted(const QString& messageId);
    void speakingFinished(const QString& messageId);
    void contextChanged(const QString& newContext);
    void volumeChanged(float volume);
    void speedChanged(float speed);
    void enabledChanged(bool enabled);
    void voiceChanged(const QString& voiceId);
    void errorOccurred(const QString& error);

private:
    VoiceAssistant(QObject* parent = nullptr);
    ~VoiceAssistant() = default;
    VoiceAssistant(const VoiceAssistant&) = delete;
    VoiceAssistant& operator=(const VoiceAssistant&) = delete;

    struct VoiceSample {
        QString path;
        QString text;
        float duration;
        QVariantMap metadata;
    };

    struct QueuedMessage {
        QString messageId;
        QVariantMap params;
        bool isPriority;
    };

    // Media playback
    std::unique_ptr<QMediaPlayer> player_;
    std::unique_ptr<QAudioOutput> audioOutput_;
    
    // Voice configuration
    QString currentVoiceId_;
    QString currentContext_;
    float volume_;
    float speed_;
    bool enabled_;
    
    // Voice samples and queues
    QMap<QString, VoiceSample> voiceSamples_;
    QMap<QString, QStringList> contextHints_;
    QQueue<QueuedMessage> messageQueue_;
    
    // Internal methods
    void processNextMessage();
    void loadVoiceSample(const QString& sampleId, const QString& path);
    QString findBestMatch(const QString& messageId, const QVariantMap& params);
    void handlePlaybackStatus(QMediaPlayer::MediaStatus status);
    
private slots:
    void onPlaybackStateChanged(QMediaPlayer::PlaybackState state);
    void onMediaStatusChanged(QMediaPlayer::MediaStatus status);
    void onErrorOccurred(QMediaPlayer::Error error, const QString& errorString);
};
