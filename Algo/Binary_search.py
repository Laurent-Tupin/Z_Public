
'''
In a nutshell, this search algorithm takes advantage of a collection of elements that is already sorted 
    by ignoring half of the elements after just one comparison. 

Compare x with the middle element.
    If x matches with the middle element, we return the mid index.
    Else if x is greater than the mid element, then x can only lie in the right (greater) half subarray after the mid element. 
    Then we apply the algorithm again for the right half.
    Else if x is smaller, the target x must lie in the left (lower) half. So we apply the algorithm for the left half.
'''


class c_binarySearch():
    def __init__(self, arr):
        self.arr = arr
        self.nbIter = 0
        self.low = 0
        self.high = len(arr) - 1
        
    def lookFor(self, x_toLookFor):
        self.x_toLookFor = x_toLookFor
        int_arg = self.LoopToLook(self.arr, self.x_toLookFor, self.low, self.high)
        self.int_arg = int_arg
        print('int_arg: ', int_arg)
        print('arr: ',  list(self.arr[int_arg-5 : int_arg + 5]))
        print('nbIter: ', self.nbIter)
        
    def NotFound(self, low, high):
        if high < low:
            return -1
        
    def LoopToLook(self, arr, x_toLookFor, low, high):
        if self.NotFound(low, high) == -1:
            return -1
        self.nbIter = self.nbIter + 1
        # Take the index in th middle
        mid = (high + low) // 2
        # If element is present at the middle itself
        if arr[mid] == x_toLookFor:
            return mid
        # If element is smaller than mid, then it can only be present in left subarray
        elif arr[mid] > x_toLookFor:
            return self.LoopToLook(arr, x_toLookFor, low, mid - 1)
        else:
            return self.LoopToLook(arr, x_toLookFor, mid + 1, high)


arr = range(1000000)
inst_binarySearch = c_binarySearch(arr)
inst_binarySearch.lookFor(254698)







