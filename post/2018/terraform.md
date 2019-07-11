## 代码及架构: terraform

公司最近用上了terraform, 新建服务, 更改配置, 增加SG都要通过他进行.



terraform是个什么东西呢? 想一下, 其实就是在各个云平台提供的API只上, 搞出来一个抽象层. 

那用terraform代码的方式写出来, 有什么好处呢?

1. 变更时候方便检查, 会打印出来要发生哪些变更. 如果出错怎么回滚, 保证升级万无一失.
2. review, 可以下放权限给dev去修改架构资源, 而只有有权限的人才可以review更改, 然后执行. 极大减轻了工作量, 还让dev更了解架构. 



note: 

1. [官方hello_word](https://learn.hashicorp.com/terraform/getting-started/install)
2. 一定要用JB平台下的, 插件. 自动格式化, 跳转...... 神兵利器.
3. [aws_resource](https://www.terraform.io/docs/providers/aws/r/elb.html)
4. [所有关键字](https://www.terraform.io/docs/configuration/data-sources.html)

### 语法

#### provider: 指定云平台及其配置

这个对应那个云平台

```
provider "aws" {
  access_key = "ACCESS_KEY_HERE"
  secret_key = "SECRET_KEY_HERE"
  region     = "us-east-1"
}

A provider is responsible for creating and managing resources. Multiple provider blocks can exist if a Terraform configuration is composed of multiple providers, which is a common situation.

就是配置一些通用的东西, 对于aws, 可以不hard code, 而是让其在~/.aws/credentials里面找.
```

#### resource: 定义资源的最小单位

```
resource "aws_instance" "example" {
  ami           = "ami-2757f631"
  instance_type = "t2.micro"
}

The resource block defines a resource that exists within the infrastructure. A resource might be a physical component such as an EC2 instance, or it can be a logical resource such as a Heroku application.

"aws_instance": resource type
	aws_ 前戳告诉terraform, 是操作aws的资源
"example": resource name


```

#### 依赖

- 显示: 使用 `depends_on` , 强调顺序. 必须要在依赖之后创建/销毁.

- 隐式: 通过表达式引用其他resource: `${aws_instance.example.id}`



#### provisioner: 提供命令处理

```
resource "aws_instance" "example" {
  ami           = "ami-b374d5a5"
  instance_type = "t2.micro"

  provisioner "local-exec" {
    command = "echo ${aws_instance.example.public_ip} > ip_address.txt"
  }
}
```

提供一种编程手段, 去操控资源数据. 上面的是在执行apple命令的机器上, 创建一个ip_address.txt, 然后将其IP地址写进去. 更高级的用法, 可以将IP写入etcd啥的 .....服务重启, 自动发现.

如果provisioner失败, 创建操作不会回滚(官方解释什么因为计划说要创建,没说要删除--), 而是会被标记成被污染.

### variable: 暴露变量允许外部传值

为了解决hardcode, 减少重复, 增加可移植性. 需要将变量抽出来.

声明变量

```python
variable "access_key" {}
variable "secret_key" {}
variable "region" {
  default = "us-east-1"
}

varibale 就是在声明一个变量, 如果写了default, 那么他是可有可无的. 如果没有写. 那么plan都不会通过, 因为没有赋值.
```

使用变量

```python
provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}
```

给变量分配值

1. 

   ```python
   $ terraform apply \
     -var 'access_key=foo' \
     -var 'secret_key=bar'
   ```

2. `TF_VAR_access_key`  `TF_VAR_name`

3. file: 

   ```python
   terraform.tfvars
   
   access_key = "foo"
   secret_key = "bar"
     
   terraform.tfvars or *.auto.tfvars present in the current directory, Terraform automatically loads them to populate variables. else use --var-file
   
   $ terraform apply \
     -var-file="secret.tfvars" \
     -var-file="production.tfvars"
   ```

4. ui input, 命令行会问你

5. 使用module, 从外部传过来(最经常的使用方式)

#### data: 

这个命令提供一种方式来筛选资源, 然后暴露出来, 给其他基础设施用, 这样可以再不知道其他基础设施具体ID的情况下引用.

```python
# Find the latest available AMI that is tagged with Component = web
data "aws_ami" "web" {
  filter {
    name   = "state"
    values = ["available"]
  }

  filter {
    name   = "tag:Component"
    values = ["web"]
  }

  most_recent = true
}

resource "aws_instance" "web" {
  ami           = "${data.aws_ami.web.id}"
  instance_type = "t1.micro"
}
```



#### local

这个是真的指定变量, 只能在同级目录下使用. 和variable的用法完全不同.

```python
# Ids for multiple sets of EC2 instances, merged together
locals {
  instance_ids = "${concat(aws_instance.blue.*.id, aws_instance.green.*.id)}"
}

# A computed default name prefix
locals {
  default_name_prefix = "${var.project_name}-web"
  name_prefix         = "${var.name_prefix != "" ? var.name_prefix : local.default_name_prefix}"
}

# Local values can be interpolated elsewhere using the "local." prefix.
resource "aws_s3_bucket" "files" {
  bucket = "${local.name_prefix}-files"
  # ...
}
```



### module

模块化, 复用, 优化架构

非常牛逼. 比方说你要搞一个Redis集群, 这里面工程很大, 要搞EC2, 要搞SG, IP, 角色乱七八糟的, 这些很大程度上都是重复代码, 这个时候,如果有一个人写了一个module, 你只需要使用它的module, 定义好输入(比如你要几个机器的集群), bingo, 把输出都写到一个文件里, 集群就建立好了!!! 那个文件可以分享给dev, 然后就可以开发了. 这么看来, 代码及架构绝对是未来.

```python
module "consul" {
  source  = "hashicorp/consul/aws"
  servers = 5
}
```



### terrform 做backend

grab使用企业版的terrformhttps://www.terraform.io/docs/backends/types/terraform-enterprise.html

就是用他们的云服务来存一些数据

```
terraform {
  backend "atlas" {
    name = "example_corp/networking-prod"
    address = "https://app.terraform.io" # optional
  }
}

data "terraform_remote_state" "foo" {
  backend = "atlas"
  config {
    name = "example_corp/networking-prod"
  }
}
```





### 命令

#### init

`terraform init`, which initializes various local settings and data that will be used by subsequent commands.

#### apply

会先plan, 然后问你要不要要不要真的执行

#### destory

会删除所有的资源, 按照必要的顺序,要删除的资源会用`-`标记.

#### plan

`+`: 表示新建一个资源

`-/+`: 表示先destroy然后在recreate这个资源, 而不是 in-place.