#pragma once

#include "Diagram.hpp"
#include <memory>
#include <vector>
#include <string>
#include <map>

namespace uml {

class State : public Element {
public:
    State(const std::string& name)
        : Element(name, ElementType::COMPONENT),
          isInitial_(false),
          isFinal_(false) {}

    void setInitial(bool isInitial) { isInitial_ = isInitial; }
    void setFinal(bool isFinal) { isFinal_ = isFinal; }
    
    bool isInitial() const { return isInitial_; }
    bool isFinal() const { return isFinal_; }

    void addEntryAction(const std::string& action) {
        entryActions_.push_back(action);
    }

    void addExitAction(const std::string& action) {
        exitActions_.push_back(action);
    }

    void addDoActivity(const std::string& activity) {
        doActivities_.push_back(activity);
    }

    const std::vector<std::string>& getEntryActions() const { return entryActions_; }
    const std::vector<std::string>& getExitActions() const { return exitActions_; }
    const std::vector<std::string>& getDoActivities() const { return doActivities_; }

private:
    bool isInitial_;
    bool isFinal_;
    std::vector<std::string> entryActions_;
    std::vector<std::string> exitActions_;
    std::vector<std::string> doActivities_;
};

class Transition : public Element {
public:
    Transition(const std::string& name,
              std::shared_ptr<State> source,
              std::shared_ptr<State> target)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target) {}

    void setTrigger(const std::string& trigger) { trigger_ = trigger; }
    void setGuard(const std::string& guard) { guard_ = guard; }
    void setEffect(const std::string& effect) { effect_ = effect; }

    const std::string& getTrigger() const { return trigger_; }
    const std::string& getGuard() const { return guard_; }
    const std::string& getEffect() const { return effect_; }

    std::shared_ptr<State> getSource() const { return source_; }
    std::shared_ptr<State> getTarget() const { return target_; }

private:
    std::shared_ptr<State> source_;
    std::shared_ptr<State> target_;
    std::string trigger_;
    std::string guard_;
    std::string effect_;
};

class CompositeState : public State {
public:
    CompositeState(const std::string& name)
        : State(name) {}

    void addSubstate(std::shared_ptr<State> state) {
        substates_.push_back(state);
    }

    const std::vector<std::shared_ptr<State>>& getSubstates() const {
        return substates_;
    }

private:
    std::vector<std::shared_ptr<State>> substates_;
};

class StateMachine : public Diagram {
public:
    StateMachine(const std::string& name)
        : Diagram(name, DiagramType::STATE_MACHINE) {}

    void addState(std::shared_ptr<State> state) {
        states_.push_back(state);
        addElement(state);
    }

    void addTransition(std::shared_ptr<Transition> transition) {
        transitions_.push_back(transition);
        addElement(transition);
    }

    std::shared_ptr<State> getInitialState() const {
        for (const auto& state : states_) {
            if (state->isInitial()) {
                return state;
            }
        }
        return nullptr;
    }

    std::vector<std::shared_ptr<State>> getFinalStates() const {
        std::vector<std::shared_ptr<State>> finals;
        for (const auto& state : states_) {
            if (state->isFinal()) {
                finals.push_back(state);
            }
        }
        return finals;
    }

    const std::vector<std::shared_ptr<State>>& getStates() const {
        return states_;
    }

    const std::vector<std::shared_ptr<Transition>>& getTransitions() const {
        return transitions_;
    }

private:
    std::vector<std::shared_ptr<State>> states_;
    std::vector<std::shared_ptr<Transition>> transitions_;
};

} // namespace uml
