STEPS 

1. Setting out aims and objectives of the project to make sure it meet stakeholders requirements to the letter.
2. designing the project architecture and data flow for the etl 
3. Investigating the data and designing the dimensional model to fit the business requirements in accordance to the aims and objectives of the project.
4. Initializing terraform as iaC to manage aws cloud resources and services needed.
5. aws configure to set aws credentials like access key and security key through the CLI
6. terraform init, terraform plan, terraform apply. 
7. Cross-check the resources created and test it is viable and in accordance with your data model.
8. A python script is then used to create the data-warehouse tables as outlined int the dimensional model. The scrispt makes use of 'Redshift-data' which is an API that lets you connect directly to your redshift as long as the aws CLI is appropraitely configured.
NOTE: you have to give the right permission to the IAM role or user used so it allows connection to Redshift and the API which is 'redshift-data'
NOTE: Using redshift-data API is a modern approach and safer and will not expose any of your credentials..
9. Once that is done and verified, you can then head to creating the actual etl pipeline. 
10. 