## professional

### 模块化

作用域 功能 职责



- 确保代码易于理解
- 确保功能的封装性
- 确保系统组件间的交互具有约束性



原则:

- 无环依赖原则. 单向, 一定不可以打破

- 稳定性依赖原则. 让不太稳定的代码依赖较为稳定的代码

- [单一职责原则.](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) 

    - 每个软件模块都应有一个且只有一个更改理由. 
    - 将因相同原因而发生变化的事物聚集在一起。分开那些由于不同原因而改变的事物。
    - 如果更改一个东西只影响一个非常小的模块, 那么就是好的模块

    > This is the reason we do not put SQL in JSPs. This is the reason we do not generate HTML in the modules that compute results. This is the reason that business rules should not know the database schema. This is the reason we *separate concerns*.







###  领域驱动设计方法



### Naked objects 裸对象模型

通用用户界面并不依赖于代码生成：它是动态创建的。在运行时，框架使用了反射技术将领域对象呈现在用户界面上。

这要求业务逻辑必须全部写在domain objects上, 然后用户界面被抽象成一个domain object.最后一步是自动创建用户界面