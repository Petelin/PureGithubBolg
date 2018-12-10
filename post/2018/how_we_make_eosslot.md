## 我们是如何做一个区块链游戏的



### 历史记录

1. 保存到表里, RAM消耗太多
2. 通过转账记录倒推, 然后用socket传给前端. 代码太麻烦,引入新的系统需要维护
3. 完美的: https://eosflare.io/account/luckyslotlog. 只需要主账号一点资源. 注意设置权限, 只允许调用者调用. 否则会记录就乱了.
4. 

### 随机数问题

1. 有且仅有使用链上随机数是对交易者负责, 项目方安心的唯一方法
2. 接口不可能提供随机数, 因为分布式每个人的random不一样, 而合约要保证幂等性.(这个原因存疑)
3. 一个action也没法拿到transaction的一些信息,所以单人生成随机数目前是不可能的
4. 多个人参与一个游戏, 每个人提供公约和msg就可以了
5. 单个人参与游戏, 只能是和项目方对赌
   1. 开奖过程一定是由项目方来完成的.
   2. 方式
      1. 使用用户当时转账的ID作为随机数
      2. transaction id + user random id
      3. (user random id + transaction time) signed by 项目方, 同时项目方提供公约验证



3个方式由https://slot.nblab.io/提供. 分析文章在https://www.nblab.io/rng



eosslotcode3: 5KbdUNsQcsFWL6FZzTQDLziKpAwotPi4LdWswDNRbRbiTnKoDHU

log:   5KRhzFy7YkpDnhBdpBSrbGwZMGM3e7NhDBLcTGoN2oNGxiHF2J1

### 执行

```shell
cleos create account eosio eosio.token \
        EOS5dSj9KKpRiuDw8a8MP2B74RxheWAVZayd2z2F7bSJtjU3dHq6t \
        EOS5dSj9KKpRiuDw8a8MP2B74RxheWAVZayd2z2F7bSJtjU3dHq6t
        
cleos create account eosio exchange \
        EOS5dSj9KKpRiuDw8a8MP2B74RxheWAVZayd2z2F7bSJtjU3dHq6t \
        EOS5dSj9KKpRiuDw8a8MP2B74RxheWAVZayd2z2F7bSJtjU3dHq6t
        
        
cleos create account eosio user \
        EOS63n7ApZAPTZS46pLi8nL7Ua5wmm7EgsjG3FTLkcYkJDrkPSRiX \
        EOS63n7ApZAPTZS46pLi8nL7Ua5wmm7EgsjG3FTLkcYkJDrkPSRiX

cleos create account eosio xxxx11111111 \
        EOS63n7ApZAPTZS46pLi8nL7Ua5wmm7EgsjG3FTLkcYkJDrkPSRiX \
        EOS63n7ApZAPTZS46pLi8nL7Ua5wmm7EgsjG3FTLkcYkJDrkPSRiX
       
cleos create account eosio tester \
        EOS8jLgxfQMo8MSH91CJoGXZHt8hfUHutEoZJDbPMe1LyDRPe4TzW \
        EOS8jLgxfQMo8MSH91CJoGXZHt8hfUHutEoZJDbPMe1LyDRPe4TzW
        
cleos create account eosio hello.code \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV

cleos create account eosio eosslotcode2 \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV
        
cleos create account eosio eosslotloger \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV \
        EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV      

echo "创建系统币"
cleos set contract eosio.token /Users/xiaolin.zhang/Documents/github/eos/contracts/eosio.token -p eosio.token@active

cleos push action eosio.token create \
        '{"issuer":"eosio", "maximum_supply":"1000000000.0000 EOS"}' \
        -p eosio.token@active

cleos push action eosio.token issue '[ "user", "10000000.0000 EOS", "memo" ]' \
        -p eosio@active

cleos transfer user xxxx11111111 "100000.1000 EOS" 
cleos transfer user eosslotcode2 "100000.1000 EOS" 
cleos transfer user eosslotloger "100000.1000 EOS" 
cleos transfer user tester "100000.1000 EOS" 
cleos transfer user hello.code "100000.1000 EOS" 

echo "设置合约"
cleos set contract eosslotloger /Users/xiaolin.zhang/Documents/github/eosslot/log -p eosslotloger

cleos set contract eosslotcode2 /Users/xiaolin.zhang/Documents/github/eosslot/eosslot -p eosslotcode2@active ;cleos push action eosslotcode2 init '{}' -p eosslotcode2

cleos set account permission eosslotcode2 active '{"threshold": 1,"keys": [{"key": "EOS81actGNqSZxT9fdmJgasGfkPo7n2WBs34QA9MNnWyrFiBcvgrV","weight": 1}],"accounts": [{"permission":{"actor":"eosslotcode2","permission":"eosio.code"},"weight":1}]}' owner -p eosslotcode2

cleos transfer xxxx11111111 eosslotcode2 "0.1000 EOS" "seed:b2cd3ea401d963b6fa75dd776a6397b77aef6623f9fabd4aa5c56f695b309af7"

cleos push action eosslotcode2 reveal '{"id": 0, "pub_key": "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV", "sig": "SIG_K1_KY6BXiZDaDm9QMKmQPr2xp9dstDgmHLkVTi4rED3DkWYTruu1D5oyU96njrpds1G7n7fW3HPBRED8Fs6b3t22QpM3iMGcu", "block_id": "011cab4d7523a59b373d324daec6d0d6ced88f7e2bb4a5782dcb308327d0715d"}' -p eosslotcode2
        
```

