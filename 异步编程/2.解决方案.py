#异步编程解决的就是各个(i/o)任务之间的调度问题，当一个任务执行时，进入等待，此时cpu空闲，其他任务可以执行，等到等待的任务完成后再继续执行
#异步编程主要利用事件循环(event loop）来实现任务的调度,在之前的编程中，任务的运行顺序是由我们来决定的，而在异步编程中，任务的运行顺序是由事件循环来决定的
#我们需要先创建一个事件循环，然后把各个任务注册到事件循环内，最后启动循环即可实现调度

#规则
#1.定义各个任务必须要用async def来定义，表示这是一个异步函数 ，可以在等待其完成时，程序转去执行其他操作，由循环事件去调度
#2.异步函数的调用必须要用await来调用，在需要进行调度的地方前面加上await，表示这里在执行时可以进行调度，当调度结束之后，再回来查看这段代码是否执行(i/o)完毕，如果执行完毕，再继续执行后面的代码
#3.await后面的对象必须是(一个可等待对象(协程对象、Future对象、Task对象))，用async def 定义的对象，否则会报错


import time

import asyncio
#main 开始 -- task1 开始 -- task2 开始 -- task2 结束 -- task1 结束 -- Result 1: 10 Result 2: 20 -- main 结束


async def task1():
    print('task1 开始')
    await asyncio.sleep(5)  #time.sleep(5)并不是由async def定义的对象，所以不能接在await后面，而应该使用asyncio.sleep(5)
    print('task1 结束')
    return 10

async def task2():
    print('task2 开始')
    await asyncio.sleep(3)
    print('task2 结束')
    return 20

async def main():
    print('main 开始')
    #在主任务中，把前面定义的各个子任务注册到事件循环中，等待事件循环去调度


    #注册(写入)之前需要先获取到事件循环对象,类似于继承
    event_loop = asyncio.get_event_loop()
    #利用async def定义好task之后，只是确保它能够被调度，但是如果你不把它写入事件循环让事件循环去调度，而直接调用task1() (另外，由于你已经把task定义成了async def，你在调用时必须要加上awai,不加await直接调用会返回协程对象类型)
    #先result1 = await t1，再result1 = await t1，其结果还是你手动去调度了，先去执行task1，执行完了再去执行task2，结果和问题.py中的结果一样，就是你只是赋予了他能力，却没有使用这个能力
    t1 = event_loop.create_task(task1())#写入task1到事件循环中
    t2 = event_loop.create_task(task2())#写入task2到事件循环中

    #注意，在执行await t1时，由于task1,task2都已经被加入到事件循环中，并且他们可切换，因此，在执行await asyncio.sleep(5)时，会挂起，然后同时去执行task2，返回值，然后再回来执行task1
    #因此执行完await t1之后，task1和task2都已经执行完毕了，所以再去执行await t2时，会直接返回结果
    result1 =await t1()#之前利用async def 定义完task之后，这里调用就需要加上await
    print(f"Result 1: {result1}")
    result2 =await t2()#等待task2执行完毕
    print(f"Result 2: {result2}")
    
    #以上的代码可以使用两行代码进行简洁描述
    #result = await asyncio.gather(task1(), task2())#gather()方法可以先获取到事件循环，然后把多个任务同时注册到事件循环中，并且等待所有任务执行完毕，返回一个列表，列表中的元素就是各个任务的返回值,然后加上await即可
    #print(f"Results: {result}")#result是一个列表，里面的元素就是各个任务的返回值

    print('main 结束')

if __name__ == "__main__":
    start_time = time.time()#time.time()表示获取当前时间的时间戳，单位为秒。
    #这里是程序的入口，在入口处需要先创建事件循环，然后启动事件循环
    
    #event_loop = asyncio.get_event_loop()#创建事件循环
    #event_loop.run_until_complete(main())#启动事件循环，直到main()执行完毕(创建完事件循环之后，需要执行一个主任务，而在主任务里面去执行子任务)注意这里一定要写main()，而不能用main
    asyncio.run(main())#asyncio.run()会自动创建事件循环，并在main()执行完毕(main()就是事件入口)后关闭事件循环，相较于上面的写法更加简洁
    #这里其实在创建，启动时间循环时，也同时把main()注册进事件循环了，把他作为事件入口，主任务，然后在主任务里面又可以去注册各个子任务
    print(f"Total time taken: {time.time() - start_time}")


#前提：已经使用asyncio.run(main())创建了一个事件循环，并且main函数是一个异步函数，然后将main函数注册到该事件循环中作为主任务

