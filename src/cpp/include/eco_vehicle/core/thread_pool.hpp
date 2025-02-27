#pragma once

#include <queue>
#include <thread>
#include <mutex>
#include <future>
#include <functional>
#include <condition_variable>
#include <vector>
#include <memory>
#include "eco_vehicle/core/logging.hpp"

namespace eco_vehicle {
namespace core {

/**
 * @brief High-performance thread pool for parallel task execution
 */
class ThreadPool {
public:
    /**
     * @brief Initialize thread pool with specified number of threads
     * @param num_threads Number of worker threads
     */
    explicit ThreadPool(size_t num_threads = std::thread::hardware_concurrency())
        : stop_(false) {
        for (size_t i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex_);
                        condition_.wait(lock, [this] {
                            return stop_ || !tasks_.empty();
                        });
                        
                        if (stop_ && tasks_.empty()) {
                            return;
                        }
                        
                        task = std::move(tasks_.front());
                        tasks_.pop();
                    }
                    task();
                }
            });
        }
    }
    
    /**
     * @brief Enqueue task for execution
     * @param f Function to execute
     * @param args Arguments for function
     * @return Future containing the result
     */
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args) 
        -> std::future<typename std::result_of<F(Args...)>::type> {
        using return_type = typename std::result_of<F(Args...)>::type;
        
        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        
        std::future<return_type> res = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            if (stop_) {
                throw std::runtime_error("enqueue on stopped ThreadPool");
            }
            
            tasks_.emplace([task]() { (*task)(); });
        }
        condition_.notify_one();
        return res;
    }
    
    /**
     * @brief Get current queue size
     * @return Number of pending tasks
     */
    size_t queue_size() const {
        std::unique_lock<std::mutex> lock(queue_mutex_);
        return tasks_.size();
    }
    
    /**
     * @brief Get number of worker threads
     * @return Number of threads
     */
    size_t thread_count() const {
        return workers_.size();
    }
    
    /**
     * @brief Stop all threads and clear queue
     */
    void stop() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            stop_ = true;
        }
        condition_.notify_all();
        for (std::thread& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }
    
    /**
     * @brief Destructor ensures all threads are stopped
     */
    ~ThreadPool() {
        stop();
    }

private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    
    mutable std::mutex queue_mutex_;
    std::condition_variable condition_;
    bool stop_;
};

} // namespace core
} // namespace eco_vehicle
