#pragma once

#include <cstddef>
#include <vector>
#include <mutex>
#include <memory>
#include <type_traits>
#include "eco_vehicle/core/logging.hpp"

namespace eco_vehicle {
namespace core {

/**
 * @brief High-performance memory pool for fixed-size allocations
 * @tparam T Type of objects to allocate
 * @tparam BlockSize Number of objects per block
 */
template<typename T, size_t BlockSize = 4096>
class MemoryPool {
    static_assert(std::is_trivially_destructible<T>::value, 
                  "T must be trivially destructible");
public:
    /**
     * @brief Initialize memory pool
     * @param initial_blocks Initial number of blocks to allocate
     */
    explicit MemoryPool(size_t initial_blocks = 1)
        : current_block_(0)
        , current_slot_(BlockSize) {
        grow(initial_blocks);
    }
    
    /**
     * @brief Allocate memory for single object
     * @return Pointer to allocated memory
     */
    T* allocate() {
        std::lock_guard<std::mutex> lock(mutex_);
        
        if (current_slot_ >= BlockSize) {
            if (current_block_ + 1 >= blocks_.size()) {
                grow(1);
            }
            ++current_block_;
            current_slot_ = 0;
        }
        
        return &blocks_[current_block_][current_slot_++];
    }
    
    /**
     * @brief Allocate memory for multiple objects
     * @param n Number of objects
     * @return Pointer to allocated memory
     */
    T* allocate_many(size_t n) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        // If request is larger than block size, allocate directly
        if (n > BlockSize) {
            auto block = std::make_unique<T[]>(n);
            large_allocations_.push_back(std::move(block));
            return large_allocations_.back().get();
        }
        
        // If current block doesn't have enough space, move to next
        if (current_slot_ + n > BlockSize) {
            if (current_block_ + 1 >= blocks_.size()) {
                grow(1);
            }
            ++current_block_;
            current_slot_ = 0;
        }
        
        T* result = &blocks_[current_block_][current_slot_];
        current_slot_ += n;
        return result;
    }
    
    /**
     * @brief Reset pool to initial state
     */
    void reset() {
        std::lock_guard<std::mutex> lock(mutex_);
        current_block_ = 0;
        current_slot_ = 0;
        large_allocations_.clear();
    }
    
    /**
     * @brief Get memory usage statistics
     * @return Pair of (used bytes, total bytes)
     */
    std::pair<size_t, size_t> get_stats() const {
        std::lock_guard<std::mutex> lock(mutex_);
        size_t used = (current_block_ * BlockSize + current_slot_) * sizeof(T);
        size_t total = blocks_.size() * BlockSize * sizeof(T);
        
        for (const auto& block : large_allocations_) {
            used += sizeof(T) * BlockSize;
            total += sizeof(T) * BlockSize;
        }
        
        return {used, total};
    }
    
    /**
     * @brief Destructor frees all allocated memory
     */
    ~MemoryPool() = default;

private:
    std::vector<std::unique_ptr<T[]>> blocks_;
    std::vector<std::unique_ptr<T[]>> large_allocations_;
    size_t current_block_;
    size_t current_slot_;
    mutable std::mutex mutex_;
    
    /**
     * @brief Grow pool by specified number of blocks
     * @param count Number of blocks to add
     */
    void grow(size_t count) {
        for (size_t i = 0; i < count; ++i) {
            blocks_.push_back(std::make_unique<T[]>(BlockSize));
        }
    }
};

} // namespace core
} // namespace eco_vehicle
