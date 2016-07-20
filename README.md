Glomex Cloud Deployment Tools
===============================

version number: 0.0.26

author: Glomex Data Platform Team

Overview
--------

These tools have emerged from our experiences while working extensively with
Cloudformation, AWS Lambda, API Gateway and CodeDeploy

Installation / Usage
--------------------

All gcdt packages live in a private PyPi repository. See [reposerver](http://reposerver-prod-eu-west-1.infra.glomex.cloud/pypi/) for instructions.

Install the package:

    $ pip install gcdt

The repo also has prerelease packages you can use for testing new features or bug fixes:

    $ pip install --pre gcdt


Contributing
------------

If you find any bugs or if you need new features please feel free to issue a pull request with your changes.

Issues and Feature Requests
-------

Please open a GitHub issue for any bug reports and feature requests.

## Common for all Tools
- All tools imply that your working directory is the directory that contains the artifact you want to work with.
- Furthermore you are responsible for supplying a valid set of AWS credentials. A good tool is [aws-mfa](https://pypi.python.org/pypi/aws-mfa/0.0.5)
- You you need to set an environment variable "ENV" which indicates the account/staging area you want to work with. This parameter tells the tools which config file to use. Basically something like settings_$(ENV).conf is evaluated in the configuration component.
1. All tools use the config_reader module from [glomex-utils](https://github.com/glomex/glomex-utils). This offers some convenient features like looking up values from other CloudFormation stacks, fetching credentials stored in credstash. See the repo documentation for details.

## Cloudformation Deploy Tool  
### kumo (雲 from Japanese: cloud)

### Usage

To see available commands, call kumo without any arguments:

```bash
$kumo
Usage:
        kumo deploy [--override-stack-policy]
        kumo list
        kumo delete -f
        kumo generate
        kumo validate
        kumo scaffold [<stackname>]
        kumo configure
        kumo preview
        kumo version
```

### Commands

#### deploy
will create or update a CloudFormation stack

to be able to update a stack that is protected by a stack policy you need to supply "--override-stack-policy"

#### list
will list all available CloudFormation stacks

#### delete
will delete a CloudFormation stack

#### generate
will generate the CloudFormation template for the given stack and write it to your current working directory.

#### validate
will validate your CloudFormation template. Warning: deploys can still fail

#### scaffold
create a new CloudFormation stack in your current working directory from a CookieCutter template

#### configure
you need to run this on first run

#### preview
will create a CloudFormation ChangeSet with your current changes to the template

#### version
will print the version of gcdt you are using

### Folder Layout

The folder layout looks like this:


cloudformation.py -> creates troposphere template, needs a method like this:

``` python
def generate_template():
    return t.to_json()
```

settings_dev.conf -> settings for dev in [hocon](https://github.com/typesafehub/config/blob/master/HOCON.md) format, needs to include all parameters for the cloudformation template + stack name

settings_prod.conf -> settings for prod in [hocon](https://github.com/typesafehub/config/blob/master/HOCON.md) format, needs to include all parameters for the cloudformation template + stack name

#### Config file example

```json
cloudformation {
  StackName = "sample-stack"

}
```

You can create a new folder with this structure by calling `kumo scaffold`.

### Howto
1. create a new local folder from the template: `kumo scaffold`
2. fill `cloudformation.py`with the contents of your stack
3. fill `settings_ENV.conf`with valid parameters for your CloudFormation template
4. call `kumo validate`to check your template for errors
5. call `kumo deploy`to deploy your stack to AWS

### Hooks
kumo offers numerous hook functions that get called during the lifecycle of a kumo run:

* pre_hook()
  * gets called before everything else - even config reading. Useful for e.g. creating secrets in credstash if they don't exist
* pre_create_hook()
  * gets called before a stack is created
* pre_update_hook()
  * gets called before a stack is updated
* post_create_hook()
  * gets called after a stack is created
* post_update_hook()
  * gets called after a stack is updated
* post_hook()
  * gets called after a stack is either updated or created

You can basically call any custom code you want. Just implement the function in
cloudformation.py

### Stack Policies
kumo does offer support for stack policies. It has a default stack policy that will get applied to each stack:

```json
{
          "Statement" : [
            {
              "Effect" : "Allow",
              "Action" : "Update:Modify",
              "Principal": "*",
              "Resource" : "*"
            },
            {
              "Effect" : "Deny",
              "Action" : ["Update:Replace", "Update:Delete"],
              "Principal": "*",
              "Resource" : "*"
            }
          ]
        }        
```
This allows an update operation to modify each resource but disables replacement or deletion. If you supply "--override-stack-policy" to kumo then it will use another default policy that gets applied during updates and allows every operation on every resource:


```json
{
          "Statement" : [
            {
              "Effect" : "Deny",
              "Action" : "Update:*",
              "Principal": "*",
              "Resource" : "*"
            }
          ]
        }
```

If you want to lock down your stack even more you can implement two functions in your cloudformation.py file:

* get_stack_policy()
* * the actual stack policy for your stack
* get_stack_policy_during_update()
* * the policy that gets applied during updates

These should return a valid stack policy document which is then preferred over the default value. 


## API Gateway Deploy Tool
### yugen (幽玄 from Japanese: “dim”, “deep” or “mysterious”)

### Usage

To see available commands, call this:
```bash
	$yugen
  Usage:
        yugen deploy
        yugen delete -f
        yugen export
        yugen list
        yugen apikey-create <keyname>
        yugen apikey-list
        yugen apikey-delete
        yugen version
```

#### deploy
creates/updates an API from a given swagger file

#### export
exports the API definition to a swagger file

#### list
lists all existing APIs

#### apikey-create
creates an API key

#### apikey-list
lists all existing API keys

#### apikey-delete
deletes an API key

#### version
will print the version of gcdt you are using

### Folder Layout

swagger.yaml -> API definition in swagger with API Gateway extensions

api.conf -> settings for the API which is needed for wiring

```
api {
    name = "dp-dev-serve-api-2"
    description = "description"
    targetStage = "dev"
    apiKey = "xxx"
}

lambda {

    entries = [
      {
        name = "dp-dev-serve-api-query"
        alias = "ACTIVE"
      },
      {
        name = "dp-dev-serve-api-query-elasticsearch"
        alias = "ACTIVE"
      }
    ]

}
```


## AWS Lambda Deploy Tool
### ramuda (ラムダ from Japanese: lambda)

### Usage

To see available commands, call this:

```bash
	$ramuda
  Usage:
        ramuda bundle
        ramuda deploy
        ramuda list
        ramuda metrics <lambda>
        ramuda wire
        ramuda unwire
        ramuda delete -f <lambda>
        ramuda rollback <lambda> [<version>]
        ramuda version
```

#### bundle
zips all the files belonging to your lambda according to your config and requirements.txt and puts it in your current working directory as `bundle.zip`. Useful for debugging as you can still provide different environments.

#### deploy
deploys a lambda function to AWS. If the lambda function is non-existent it will create a new one. For an existing lambda function it checks whether code has changed and updates accordingly. In any case configuration will be updated and an alias called "ACTIVE" will be set to this version.

#### list
lists all existing lambda functions including additional information like config and active version:
```bash
dp-dev-store-redshift-create-cdn-tables
	Memory: 128
	Timeout: 180
	Role: arn:aws:iam::644239850139:role/lambda/dp-dev-store-redshift-cdn-LambdaCdnRedshiftTableCr-G7ME657RXFDB
	Current Version: $LATEST
	Last Modified: 2016-04-26T18:03:44.705+0000
	CodeSha256: KY0Xk+g/Gt69V0siRhgaG7zWbg234dmb2hoz0NHIa3A=
```

#### metrics
displays metric for a given lambda:
```bash
dp-dev-ingest-lambda-cdnnorm
	Duration 488872443
	Errors 642
	Invocations 5202
	Throttles 13
```

#### wire
"wires" the lambda function to its event configuration. This actually activates the lambda function.

#### unwire
delets the event configuration for the lambda function

#### delete
deletes a lambda function

#### rollback
sets the active version to ACTIVE -1 or to a given version

#### version
will print the version of gcdt you are using


### Folder Layout

lambda_ENV.conf -> settings for Lambda function

```json
lambda {
  name = "dp-dev-store-redshift-load"
  description = "Lambda function which loads normalized files into redshift"
  role = "arn:aws:iam::644239850139:role/lambda/dp-dev-store-redshift-cdn-lo-LambdaCdnRedshiftLoad-DD2S84CZFGT4"

  handlerFunction = "handler.lambda_handler"
  handlerFile = "handler.py"
  timeout = "180"
  memorySize = "128"
  events {
    s3Sources = [
        { bucket = "dp-dev-store-cdn-redshift-manifests", type = "s3:ObjectCreated:*", suffix = ".json" }
    ]
  }
  vpc  {
    subnetIds = ["subnet-87685dde", "subnet-9f39ccfb", "subnet-166d7061"]
    securityGroups = ["sg-ae6850ca"]
  }
}

bundling {
  zip = "bundle.zip"
  folders = [
    { source = "../redshiftcdnloader", target = "./redshiftcdnloader"}
    { source = "psycopg2-linux", target = "psycopg2" }
  ]
}

deployment {
  region = "eu-west-1"
}

```

settings_env.conf -> settings for your code


#### S3 upload
ramuda can upload your lambda functions to S3 instead of inline through the API.
To enable this feature add this to your lambda.conf:

deployment {
    artifactBucket = "7finity-$PROJECT-deployment"
}

You can get the name of the bucket from Ops and it should be part of the stack outputs of the base stack in your account (s3DeploymentBucket).

## AWS CodeDeploy Tool
### tenkai (展開 from Japanese: deployment)
### Usage

To see available commands, call this:

```bash
	$tenkai
  Usage:
        tenkai deploy
        tenkai version

```


#### deploy
bundles your code then uploads it to S3 as a new revision and triggers a new deployment

#### version
will print the version of gcdt you are using



### Folder Layout

codedeploy -> folder containing your deployment bundle

codedeploy_env.conf -> settings for your code
```json
codedeploy {
applicationName = "mep-dev-cms-stack2-mediaExchangeCms-F5PZ6BM2TI8",
deploymentGroupName = "mep-dev-cms-stack2-mediaExchangeCmsDg-1S2MHZ0NEB5MN",
deploymentConfigName = "CodeDeployDefaultemplate.AllAtOnce01"
artifactsBucket = "7finity-portal-dev-deployment"
}
```


## General advice
### Homebrew Python

If you installed Python via Homebrew on OS X and get this error:

"must supply either home or prefix/exec-prefix -- not both"

You can find a solution here:

http://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both
### Environment variables
Be sure to provide the correct environment variables (ENV=PROD/DEV/etc.)
