<!-- vue中的template,script,style分别是用来写html,javascript，css的，三个模块分别适用三种语法，另外还有多的 -->
<!-- template类似于html，用来构建框架，格式，无法接收值.script用来写函数 -->
<!-- ctrl+/可以快速进行注释，并且，在哪个模块ctrl+/会自动识别成那个模块的注释 -->
<!-- 一个vue文件对应一个大组件，export default 就是把"这个组件的定义对象"作为模块的默认导出。Vue 拿到这个对象，就知道这个组件有哪些数据、方法、模板，导出配置清单
  ，data()是其中的一个内置函数，return返回一个对象的各种数据,函数的话要加()，且不需要：，而其中的各个对象都需要加上':',用来表示默认值。而且这里为了把个人信息进行统一打包，
  还把age等信息融到了userInfo对象中-->
<!-- radio类型就是用来选择a或b,当选择男前面的圆圈时，赋值给userInfo.sex的值就是1，同理选女生赋值2-->
<!-- div 管"块"，span 管"字"。​ 需要局部包一小撮行内内容就用 span，需要一大块区域用 div -->
<!--  v-for="value in source ，即定义value循环遍历source中的变量，然后value就可以代表source中的所有元素，输出value即输出整个source中的内容
  :key表示如何区分source中的各个变量，这里由于python，java，vue用变量名就可以进行区分，因此这里区分就用skill-->
<!-- @click 是 v-on:click的简写，@input等等同理-->
<template>
  <div>
    姓名: <input v-model="username"/>{{ username }}<br/> <!--script中去定义两个对象，v-model使html的框可以连接这两个对象-->
    薪水: <input type ="number" v-model="salary"/>{{ salary }}<br/> <!--{{  }}是用于直接访问vue中的变量，{{ salary }}会显示出salary的值-->
    <button v-on:click="addSalary">提交</button><button @click ="changeUserInfo">查看个人信息</button>
  </div>
    <hr />
  <div class = "userInfo" v-if = "showUserInfo"> <!--组件加class可以用于进行css格式设计。v-if用于决定该组件是否可见，值为true即可见，false不可见，因此后面的showUserInfo应该是bool类型的-->
        <h2>个人信息</h2>
        <p>年龄：<input type = "number" v-model="userInfo.age" /></p><br />
        <p>性别: <input type = 'radio' value="1" v-model="userInfo.sex">男</input><input type = 'radio' value="2" v-model="userInfo.sex">女</input></p><br />
        <p>岗位：<select v-model="userInfo.department">
          <option value ="dev">开发</option>
          <option value ="test">测试</option>
          <option value =" maintain">运维</option>
        </select></p>
        <p>技术: <span v-for="skill in userInfo.skills" :key="skill">{{ skill }}</span></p> <!--结果会输出javapythonvue-->
        <p>新技术：<input v-model="newSkill"/><button @click="addNewSkill">添加新技术</button></p>
        <p>个人信息汇总{{ userInfo }}</p>{{ userInfo.department }}
  </div>
</template>

<script lang="ts" >
  export default{
    data(){
      return{
        username : 'hqb', //用{{username}}可以看到，当html中的username框中的值改变了，对应的script中的变量值也会发生改变
        salary : 15000,
        userInfo:{
          age : 20,
          sex : 1,
          department : '',//department接收字符串，当选择某个option时，就会传给他对应的名称/值
          skills : ['java','python','vue'],
       },
       newSkill:'',
       showUserInfo:false
      }
    },
    methods:{
      addSalary(){
        this.salary +=1000 //点击button时触发addsalary事件，该事件会引起该对象的salary数据加1000(export default导出整个对象定义模块，该对象包含username,salary，userInfo等信息）
      },
      addNewSkill(){
        if(this.newSkill)
          this.userInfo.skills.push(this.newSkill)
        },
      changeUserInfo(){
        this.showUserInfo =!this.showUserInfo;
      }
    }
  }

</script>

<style scoped>
  .userInfo{
    background-color: aliceblue;
    widows: 80%;
  }
  .userInfo span{
    background-color: aquamarine;
    margin-left: 10px;
    border: 1px;
    border-radius: 5px;
  }
</style>
