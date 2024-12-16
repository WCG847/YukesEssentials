class YMAlloc:
    """
    YMAlloc maps files and assets into virtual memory, emulating the behavior of Yuke's memory allocation
    """

    def __init__(self, total_memory=1024 * 1024 * 256):  # Default: 256 MB
        """
        Initialise the YMAlloc instance.

        :param total_memory: The total size of the virtual memory space.
        """
        self.total_memory = total_memory
        self.memory = None  # Memory is initialised lazily.
        self.free_list = [(0, total_memory)]  # List of free blocks (start, size).

    def _initialise_memory(self):
        """
        Lazily initialise the memory space to save resources until it's needed.
        """
        if self.memory is None:
            self.memory = bytearray(self.total_memory)

    @staticmethod
    def _align_size(size):
        """
        Align the size to the nearest 16-byte boundary.

        :param size: The size to align.
        :return: The aligned size.
        """
        return (size + 15) & ~15

    def allocate(self, size):
        """
        Allocate a block of virtual memory.

        :param size: The size of the memory block to allocate.
        :return: The starting address of the allocated block or None if allocation fails.
        """
        # Lazily initialise memory if not already done
        self._initialise_memory()

        # Align size to 16 bytes
        aligned_size = self._align_size(size)

        for i, (start, block_size) in enumerate(self.free_list):
            if block_size >= aligned_size:
                # Allocate memory from this block
                allocated_start = start
                remaining_size = block_size - aligned_size

                if remaining_size > 0:
                    # Update free list with remaining block
                    self.free_list[i] = (start + aligned_size, remaining_size)
                else:
                    # Remove fully allocated block from free list
                    self.free_list.pop(i)

                return allocated_start

        # Allocation failed (no suitable block)
        return None

    def free(self, address, size):
        """
        Free a previously allocated block of memory.

        :param address: The starting address of the block to free.
        :param size: The size of the block to free.
        """
        # Align size to 16 bytes
        aligned_size = self._align_size(size)

        # Insert the freed block back into the free list
        self.free_list.append((address, aligned_size))
        self.free_list.sort()  # Keep the free list ordered by address

        # Merge adjacent free blocks
        merged_free_list = []
        last_start, last_size = self.free_list[0]

        for start, block_size in self.free_list[1:]:
            if last_start + last_size == start:
                # Merge blocks
                last_size += block_size
            else:
                merged_free_list.append((last_start, last_size))
                last_start, last_size = start, block_size

        merged_free_list.append((last_start, last_size))
        self.free_list = merged_free_list

    def debug_memory(self):
        """
        Print the current state of the free list for debugging purposes.
        """
        print("Free List:")
        for start, size in self.free_list:
            print(f"Start: {start}, Size: {size}")


# Global instance of YMAlloc
ymalloc_instance = YMAlloc()


def ymalloc(size):
    """
    Global YMAlloc function to allocate memory.

    :param size: The size of the memory block to allocate.
    :return: The starting address of the allocated block or None if allocation fails.
    """
    return ymalloc_instance.allocate(size)


def yfree(address, size):
    """
    Global YFree function to free memory.

    :param address: The starting address of the block to free.
    :param size: The size of the block to free.
    """
    if address is None:
        return

    # Free memory back to the free list
    ymalloc_instance.free(address, size)

    # Debugging output (for internal verification)
    ymalloc_instance.debug_memory()


def debug_memory():
    """
    Debugging function to print the current state of virtual memory.
    """
    ymalloc_instance.debug_memory()