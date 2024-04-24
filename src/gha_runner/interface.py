from abc import ABC, abstractmethod
from dataclasses import dataclass
import boto3


class CloudDeployment(ABC):
    @abstractmethod
    def create_instance(self, count: int) -> list[str]:
        pass

    @abstractmethod
    def remove_instances(self, ids: list[str]):
        pass


@dataclass
class AWS(CloudDeployment):
    image_id: str
    instance_type: str
    subnet_id: str
    security_group_id: str
    iam_role: str
    tags: list[str]
    region_name: str

    def create_instance(self, count: int) -> list[str]:
        ec2 = boto3.client("ec2", region_name=self.region_name)
        params = {
            "ImageId": self.image_id,
            "InstanceType": self.instance_type,
            "MinCount": count,
            "MaxCount": count,
            "SubnetId": self.subnet_id,
            "SecurityGroupIds": [self.security_group_id],
            "IamInstanceProfile": {"Name": self.iam_role},
            # "TagSpecifications": self.tags,
        }
        result = ec2.run_instances(**params)
        # TODO: This might now be exactly how the result is structured
        instances = result["Instances"]
        ids = [instance["InstanceId"] for instance in instances]
        return ids

    def remove_instances(self, ids: list[str]):
        ec2 = boto3.client("ec2", self.region_name)
        params = {
            "InstanceIds": ids,
        }
        ec2.terminate_instances(**params)


class CloudDeploymentFactory:
    providers = {"aws": AWS}

    def get_provider(self, provider_name: str, **kwargs) -> CloudDeployment:
        if self.providers.get(provider_name):
            try:
                return self.providers[provider_name](**kwargs)
            except TypeError as t:
                # Raise a more informative error message
                raise TypeError(
                    f"Invalid configuration for provider {provider_name}: {t}"
                )
        else:
            raise ValueError("Invalid provider name")
