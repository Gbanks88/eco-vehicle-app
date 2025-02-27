#pragma once

#include <QString>
#include <QVector>
#include <QMap>
#include <QVariant>
#include <memory>

namespace FlowModeling {

// Forward declarations
class Activity;
class ObjectFlow;
class ControlNode;
class SignalHandler;
class DataSource;
class Buffer;
class ParameterSet;

// Base class for all flow elements
class FlowElement {
public:
    virtual ~FlowElement() = default;
    QString id() const { return m_id; }
    QString name() const { return m_name; }
    QString description() const { return m_description; }
    
protected:
    QString m_id;
    QString m_name;
    QString m_description;
};

// Activity class representing a unit of behavior
class Activity : public FlowElement {
public:
    enum class State {
        Inactive,
        Active,
        Completed,
        Failed,
        Suspended
    };
    
    Activity();
    ~Activity() override;
    
    void addInputParameter(const QString& name, const QVariant& defaultValue = QVariant());
    void addOutputParameter(const QString& name);
    void setParameterSet(std::shared_ptr<ParameterSet> params);
    void connectTo(std::shared_ptr<Activity> target, const QString& outputParam, const QString& inputParam);
    void execute();
    void suspend();
    void resume();
    void abort();
    
    State state() const { return m_state; }
    QVector<QString> inputParameters() const { return m_inputParams; }
    QVector<QString> outputParameters() const { return m_outputParams; }
    
private:
    State m_state;
    QVector<QString> m_inputParams;
    QVector<QString> m_outputParams;
    std::shared_ptr<ParameterSet> m_parameterSet;
    QVector<std::shared_ptr<ObjectFlow>> m_incomingFlows;
    QVector<std::shared_ptr<ObjectFlow>> m_outgoingFlows;
};

// Object flow for passing data between activities
class ObjectFlow : public FlowElement {
public:
    enum class Type {
        Data,
        Control,
        Event
    };
    
    ObjectFlow(Type type = Type::Data);
    ~ObjectFlow() override;
    
    void setSource(std::shared_ptr<Activity> source, const QString& outputParam);
    void setTarget(std::shared_ptr<Activity> target, const QString& inputParam);
    void setBuffer(std::shared_ptr<Buffer> buffer);
    void setTransformation(std::function<QVariant(const QVariant&)> transform);
    
    bool isValid() const;
    void activate();
    void deactivate();
    
private:
    Type m_type;
    std::shared_ptr<Activity> m_source;
    std::shared_ptr<Activity> m_target;
    QString m_sourceParam;
    QString m_targetParam;
    std::shared_ptr<Buffer> m_buffer;
    std::function<QVariant(const QVariant&)> m_transformation;
};

// Control node for managing flow logic
class ControlNode : public FlowElement {
public:
    enum class Type {
        Initial,
        Final,
        Fork,
        Join,
        Decision,
        Merge
    };
    
    ControlNode(Type type);
    ~ControlNode() override;
    
    void addIncoming(std::shared_ptr<ObjectFlow> flow);
    void addOutgoing(std::shared_ptr<ObjectFlow> flow);
    void setCondition(std::function<bool(const QVariantMap&)> condition);
    
    bool evaluate(const QVariantMap& context);
    void activate();
    
private:
    Type m_type;
    QVector<std::shared_ptr<ObjectFlow>> m_incoming;
    QVector<std::shared_ptr<ObjectFlow>> m_outgoing;
    std::function<bool(const QVariantMap&)> m_condition;
};

// Signal handler for event management
class SignalHandler : public FlowElement {
public:
    SignalHandler();
    ~SignalHandler() override;
    
    void registerSignal(const QString& signalName);
    void connectSignal(const QString& signalName, std::shared_ptr<Activity> target);
    void emit(const QString& signalName, const QVariantMap& data = QVariantMap());
    
private:
    QMap<QString, QVector<std::shared_ptr<Activity>>> m_signalConnections;
};

// Data source for external data integration
class DataSource : public FlowElement {
public:
    enum class Type {
        Database,
        File,
        Network,
        Sensor
    };
    
    DataSource(Type type);
    ~DataSource() override;
    
    void configure(const QVariantMap& config);
    void connect();
    void disconnect();
    QVariant read(const QString& query);
    void write(const QString& location, const QVariant& data);
    
private:
    Type m_type;
    QVariantMap m_config;
    bool m_connected;
};

// Buffer for temporary data storage
class Buffer : public FlowElement {
public:
    enum class Policy {
        FIFO,
        LIFO,
        Priority
    };
    
    Buffer(Policy policy = Policy::FIFO);
    ~Buffer() override;
    
    void setCapacity(int capacity);
    void push(const QVariant& data);
    QVariant pop();
    QVariant peek() const;
    bool isEmpty() const;
    bool isFull() const;
    
private:
    Policy m_policy;
    int m_capacity;
    QVector<QVariant> m_data;
};

// Parameter set for activity configuration
class ParameterSet : public FlowElement {
public:
    ParameterSet();
    ~ParameterSet() override;
    
    void addParameter(const QString& name, const QVariant& defaultValue = QVariant());
    void setValue(const QString& name, const QVariant& value);
    QVariant getValue(const QString& name) const;
    bool validate() const;
    
private:
    QMap<QString, QVariant> m_parameters;
    QMap<QString, QVariant> m_defaults;
};

// Flow modeling system manager
class FlowModelingSystem {
public:
    static FlowModelingSystem& instance();
    
    std::shared_ptr<Activity> createActivity(const QString& name);
    std::shared_ptr<ObjectFlow> createFlow(ObjectFlow::Type type);
    std::shared_ptr<ControlNode> createControlNode(ControlNode::Type type);
    std::shared_ptr<SignalHandler> createSignalHandler();
    std::shared_ptr<DataSource> createDataSource(DataSource::Type type);
    std::shared_ptr<Buffer> createBuffer(Buffer::Policy policy);
    std::shared_ptr<ParameterSet> createParameterSet();
    
    void saveModel(const QString& filename);
    void loadModel(const QString& filename);
    void validateModel();
    void executeModel();
    
private:
    FlowModelingSystem() = default;
    ~FlowModelingSystem() = default;
    
    QVector<std::shared_ptr<FlowElement>> m_elements;
};

} // namespace FlowModeling
