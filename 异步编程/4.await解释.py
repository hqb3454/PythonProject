#解释，
#1.加入到事件循环内的协程对象(定义的是异步函数，但是调用时返回的是协程对象，因此是协程对象被写入时间循环)会转换为Task对象，Task对象是事件循环内部执行的单位
#2.await后面只能跟协程对象(如await task1()，注意await asyncio.sleep(3)有所不同)，Task对象(await t1) 和 future对象
#3.当await后面跟的是协程对象时，会停止当前的协程（即当前异步函数的执行），转去执行后面协程对象的代码，实现调用的结果，因此，如果task1()没写入事件循环，而直接在main中执行 await task1(),就回去执行调用task1,并且由于没写入事件循环，不会进行调度，因此会顺序执行
#4.对于task来说，如果在装成task前的异步函数，其内部的await后面跟的是协程对象的话，那么即使是task也不会进行切换，而是一样，去执行await后面的协程对象
#5.当await后面跟的是future对象时，会挂起当前任务，转去执行其他任务，此时可以进行切换
#6.await asyncio.sleep(3)其也是协程对象（异步函数），但是在这个函数内部创建了future对象，并且有await future这段代码，因此，转去执行sleep函数时，在其内部进行了task切换


import asyncio

#task01 -- sub_task -- task02
async def task02():
    print('task02')
    return 200


async def sub_task():
    print('sub_task')
    return 100


async def task01():
    print('task01')
    #按理来说，两个加入到事件循环中的协程对象已经化为task对象，那么他们应该是可以进行调度切换的
    #但由于task01内部，其用于标识切换的await后面跟的是另一个协程对象，那么在执行task01中的await时不会切换到task02,而是去执行sub_task，直至执行结束，再去执行task02

    #await asyncio.sleep(3) 如果添加这行，那么会在这里进行task切换，因为执行sleep函数时，会执行到其内部的一句return await future代码

    result = await sub_task()
    return result


async def start():
    # 在事件循环中注册两个任务 task01 和 task02
    # 并等待两个任务的执行结果
    result = await asyncio.gather(task01(), task02())
    print(result)

if __name__ == "__main__":
    asyncio.run(start())