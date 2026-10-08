import time

def task1():
    time.sleep(5)
    return 10

def task2():
    time.sleep(3)
    return 20

def main():
    result1 = task1()
    result2 = task2()
    print(f"Result 1: {result1}")
    print(f"Result 2: {result2}")


#在python中，__name__是一个特殊的变量，它表示当前模块的名称。当一个模块被直接运行时，__name__的值为"__main__"。而当一个模块被导入到其他模块中时，__name__的值为该模块的名称。
#因此，只有当这个模块被直接运行时，才会执行if __name__ == "__main__":下的代码块。而被import时不会执行，从而避免了在导入模块时执行不必要的代码。
#另外，与c语言不同的是，python中没有main函数的概念，定义了main函数之后，它不会立即执行，只有当执行if __name__ == "__main__":时，才会执行下面的代码（此时为直接运行）
if __name__ == "__main__":
    start_time = time.time()#time.time()表示获取当前时间的时间戳，单位为秒。
    main()
    print(f"Total time taken: {time.time() - start_time}")
    #问题在于，当顺序执行时，当task1 sleep(模拟网络i/o操作)时，cpu空闲，必须等待task1执行完毕才能执行task2，导致总耗时为8秒。