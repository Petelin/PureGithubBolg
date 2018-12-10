## 文档数据库:DynamoDB

dynamo is an expressive DyanmoDB ORM which highly integrates with the official [AWS SDK](https://github.com/aws/aws-sdk-go/).

### Quick Example

```go
type User struct {
    ID        int
    Age       int
    LastName  string `json:"last_name"`
    FirstName string `json:"first_name"`
}
const partitionKey = "ID"
const RangeKey = "LastName"

// init dynamo with config and tableName
table = dynamo.DB(context.Background(), "fake-region", nil).Table(tableName)

// save one user
user := User{
    ID:        1,
    Age:       32,
    FirstName: "Dennis",
    LastName:  "Ritchie",
}
err := table.Put(&user).NotExist(partitionKey, RangeKey).Run()
if err != nil {
    return
}

// get by partitionKey and RangeKey
getUser := new(testUser)
err = table.Get(partitionKey, user.ID).Range(RangeKey, user.LastName).
Consistent(true).
Fields("ID", "first_name").
One(getUser)
if err != nil {
    return
}

// Update age field
updateCondition := expression.UpdateBuilder{}.
Set(expression.Name("Age"), expression.Value(33))
err = table.Update(partitionKey, user.ID).Range(RangeKey, user.LastName).
UpdateBuilder(updateCondition).
Run()
if err != nil {
    return
}

// also provide query, scan
```



### Problem we meet

#### 1. Hard to constuct param

in the old days, we have to create expression by hand wrting. it looks like a "assembly language". It make me code very slowly, hard to change and reuse. 



example 1:  code in `Grab-Wheels`, with those magic string `Exp` 

```go
const versionUpdateExp    = "SET DefaultJSON = :defaultJSON, ServiceConfigurationsJSON = :serviceConfigurationsJSON, UpdatedAt = :updatedAt ADD Version :incr"
const versionConditionExp = "attribute_not_exists(Version) OR Version = :version"

func (d *ddbMicroserviceConfigurations) Save(ctx context.Context, configs MicroserviceConfigurations) error {
	params := &dynamodb.UpdateItemInput{
		TableName:           aws.String(config.Config.AWS.DDB.Configs),
		UpdateExpression:    aws.String(versionUpdateExp),
		ConditionExpression: aws.String(versionConditionExp),
		ExpressionAttributeValues: map[string]*dynamodb.AttributeValue{
			":incr": {N: aws.String("1")},
			":serviceConfigurationsJSON": {S: aws.String(string(ddbutils.ToJSON(configs.ServiceConfigurations)))},
			":defaultJSON":               {S: aws.String(string(ddbutils.ToJSON(configs.DefaultConfiguration)))},
			":version":                   {N: aws.String(strconv.FormatInt(int64(configs.Version), 10))},
			":updatedAt":                 {N: aws.String(fmt.Sprintf("%d", time.Now().Unix()))},
		},
		Key: map[string]*dynamodb.AttributeValue{
			attributeNamespace: {
				S: aws.String(configs.Namespace),
			},
			attributeKey: {
				S: aws.String(configs.Key),
			},
		},
		ReturnValues: aws.String("ALL_OLD"),
	}
}
```

#### 2. Hard to use return value

old client return data with a map struct `map[string]*dynamodb.AttributeValue`.  we have to get data by a string key (rather than `A.field`) ,  and then do nil test, covert to sepcial type. all of this is not neccessory. 



example: 

```go
func configurationsFromDDB(item map[string]*dynamodb.AttributeValue) MicroserviceConfigurations {
	c := MicroserviceConfigurations{
		Namespace: *(item[attributeNamespace].S),
		Key:       *(item[attributeKey].S),
	}
	if jsonDefaultConfig := item[attributeDefaultConfigurationJSON]; jsonDefaultConfig != nil && jsonDefaultConfig.S != nil {
		_ = json.Unmarshal([]byte(*(jsonDefaultConfig.S)), &(c.DefaultConfiguration))
	}
	if item[attributePoolConfigurations] != nil {
		_ = json.Unmarshal(item[attributePoolConfigurations].B, &(c.PoolConfigurations))
	}
	if jsonServiceConfig := item[attributeServiceConfigurationsJSON]; jsonServiceConfig != nil && jsonServiceConfig.S != nil {
		_ = json.Unmarshal([]byte(*(jsonServiceConfig.S)), &(c.ServiceConfigurations))
	}
	if item[attributeVersion] != nil && item[attributeVersion].N != nil {
		version, _ := strconv.ParseInt(*(item[attributeVersion].N), 10, 32)
		c.Version = int(version)
	}
	return c
}
```



### Problem sovled

we provide a chained method calls with integrate with aws package `expression` . It provide us  `UpdateBuilder` and `ConditionBuilde` , we do not need to write string format expression.  

this is a rewrite to the first example:

```go
updateBuilder := expression.UpdateBuilder{}.
	Set(expression.Name("Age"), expression.Value(33)).
	Set(expression.Name("DefaultJSON"), expression.Value(configs.DefaultConfiguration)).
	Set(expression.Name("ServiceConfigurationsJSON"), expression.Value(configs.ServiceConfigurations)).
	Set(expression.Name("UpdatedAt"), expression.Value(configs.UpdateAt)).
	Add(expression.Name("Version"), expression.Value(1))

condition := expression.Name("Version").AttributeNotExists().Or(expression.Name("Version").Equal(configs.Version))

err = table.Update(partitionKey, configs.Namespace).Range(RangeKey, configs.Key).
	Condition(condition).
	UpdateBuilder(updateBuilder).
    ReturnValue(dynamodb.ReturnValueAllOld, nil)
	Run()
```

less code but more expressive and we remove all "magic string" construct param with a more robost way. With method hint provide by IDE, we can write those rubost code easy and quickly.

New client handle all conver detail, all user need to do is pass an interface  struct. we will fill it with response.



###  Performance

#### logic analyze

the must expencie operation will be the internet access, the second will the `marshal` and `unmarshal`

However, due to sepcial DynamoDB JSON structer, data unmarshal is even faster then JSON unmarshal. here is the benchmark result

```
goos: darwin
goarch: amd64
pkg: gitlab.myteksi.net/gophers/go/food/food-profile/db/dynamo/example
Benchmark_DDBMarshalMap-8                 100000             18291 ns/op
Benchmark_DDB_UNMarshalMap-8              100000             17999 ns/op
Benchmark_JSONMarshal-8                   500000              2745 ns/op
Benchmark_JSON_UNMarshalMap-8              20000             83945 ns/op
```

#### real performance

```
goos: darwin
goarch: amd64
pkg: gitlab.myteksi.net/gophers/go/food/food-profile/db/dynamo/example
Benchmark_CRUD_Save-8                        500           3314416 ns/op
Benchmark_CRUD_RawSave-8                     500           3360046 ns/op
Benchmark_CRUD_Get-8                        1000           2051761 ns/op
Benchmark_CRUD_RawGet-8                     1000           1919121 ns/op
```

