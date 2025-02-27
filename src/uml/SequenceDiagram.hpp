#pragma once

#include "Diagram.hpp"
#include <vector>
#include <memory>
#include <string>

namespace uml {

enum class MessageType {
    SYNCHRONOUS,
    ASYNCHRONOUS,
    REPLY,
    CREATE,
    DESTROY
};

class Lifeline : public Element {
public:
    Lifeline(const std::string& name)
        : Element(name, ElementType::CLASS),
          isActor_(false) {}

    void setActor(bool isActor) { isActor_ = isActor; }
    bool isActor() const { return isActor_; }

private:
    bool isActor_;
};

class Message : public Element {
public:
    Message(const std::string& name,
           std::shared_ptr<Lifeline> source,
           std::shared_ptr<Lifeline> target,
           MessageType type)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target),
          type_(type),
          sequenceNumber_(0) {}

    void setSequenceNumber(int number) { sequenceNumber_ = number; }
    int getSequenceNumber() const { return sequenceNumber_; }

    std::shared_ptr<Lifeline> getSource() const { return source_; }
    std::shared_ptr<Lifeline> getTarget() const { return target_; }
    MessageType getType() const { return type_; }

    void setGuard(const std::string& guard) { guard_ = guard; }
    const std::string& getGuard() const { return guard_; }

private:
    std::shared_ptr<Lifeline> source_;
    std::shared_ptr<Lifeline> target_;
    MessageType type_;
    int sequenceNumber_;
    std::string guard_;
};

class CombinedFragment : public Element {
public:
    enum class OperatorType {
        ALT,    // Alternative
        OPT,    // Optional
        LOOP,   // Loop
        PAR,    // Parallel
        CRITICAL // Critical region
    };

    CombinedFragment(const std::string& name, OperatorType op)
        : Element(name, ElementType::COMPONENT),
          operatorType_(op) {}

    void addOperand(const std::string& guard) {
        operands_.push_back(guard);
    }

    OperatorType getOperatorType() const { return operatorType_; }
    const std::vector<std::string>& getOperands() const { return operands_; }

private:
    OperatorType operatorType_;
    std::vector<std::string> operands_;
};

class SequenceDiagram : public Diagram {
public:
    SequenceDiagram(const std::string& name)
        : Diagram(name, DiagramType::SEQUENCE) {}

    void addLifeline(std::shared_ptr<Lifeline> lifeline) {
        lifelines_.push_back(lifeline);
        addElement(lifeline);
    }

    void addMessage(std::shared_ptr<Message> message) {
        messages_.push_back(message);
        addElement(message);
    }

    void addCombinedFragment(std::shared_ptr<CombinedFragment> fragment) {
        fragments_.push_back(fragment);
        addElement(fragment);
    }

    const std::vector<std::shared_ptr<Lifeline>>& getLifelines() const {
        return lifelines_;
    }

    const std::vector<std::shared_ptr<Message>>& getMessages() const {
        return messages_;
    }

    const std::vector<std::shared_ptr<CombinedFragment>>& getFragments() const {
        return fragments_;
    }

private:
    std::vector<std::shared_ptr<Lifeline>> lifelines_;
    std::vector<std::shared_ptr<Message>> messages_;
    std::vector<std::shared_ptr<CombinedFragment>> fragments_;
};

} // namespace uml
