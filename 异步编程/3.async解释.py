import asyncio

async def task():
    print('task1')

#利用async def定义完异步函数之后，是无法直接调用的，直接调用，会返回协程对象(coroutine)。异步函数的执行结果就是一个协程对象，
#而asyncio的相关函数只能接收协程对象，例如event_loop = asyncio.get_event_loop()，t1 = event_loop.create_task(task1())和asyncio.run(main())因此要加括号，main()
#而协程对象是一个还未开始的任务，都写在"代办事项"上面，需要事件循环去调度

def main():
    coro = task()

#前面，针对asyncio.run(main())，他可以创建事件循环，启动事件循环，并且读入括号内传入的协程对象，把他添加到事件循环里面
#因此，可以针对task这个异步函数，单独创建一个事件循环，并把它写入,事件循环会自动调用该函数
    asyncio.run(coro)

if __name__ == "__main__":
    main()