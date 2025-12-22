from typing import Dict, List, Optional
from httpx import Response
import json

from javelin_sdk.models import (
    Customer,
    CustomerResponse,
    AWSConfig,
    AzureConfig,
    GCPConfig,
    CloudConfigResponse,
    UsageResponse,
    AlertResponse,
    HttpMethod,
    Request,
)


class AISPMService:
    def __init__(self, client):
        self.client = client

    def _get_aispm_headers(self) -> Dict[str, str]:
        """Get headers for AISPM requests, including account_id if available."""
        headers = {}
        # Check if account_id is stored in client (set by get_javelin_client_aispm)
        account_id = getattr(self.client, "_aispm_account_id", None)
        if account_id:
            headers["x-javelin-accountid"] = account_id
            headers["x-javelin-user"] = getattr(
                self.client, "_aispm_user", "test-user"
            )
            headers["x-javelin-userrole"] = getattr(
                self.client, "_aispm_userrole", "org:superadmin"
            )
        return headers

    def _handle_response(self, response: Response) -> None:
        if response.status_code >= 400:
            try:
                error_data = response.json()
                # Handle different error response formats
                error = (
                    error_data.get("error")
                    or error_data.get("message")
                    or str(error_data)
                )
            except Exception:
                error = f"HTTP {response.status_code}: {response.text}"
            raise Exception(f"API error: {error}")

    # Customer Methods
    def create_customer(self, customer: Customer) -> CustomerResponse:
        request = Request(
            method=HttpMethod.POST,
            route="v1/admin/aispm/customer",
            data=customer.dict(),
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return CustomerResponse(**response.json())

    def get_customer(self) -> CustomerResponse:
        request = Request(
            method=HttpMethod.GET,
            route="v1/admin/aispm/customer",
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        response_data = response.json()
        # Check if response indicates failure (even with 200 status)
        if isinstance(response_data, dict) and response_data.get("success") is False:
            error_msg = (
                response_data.get("message")
                or response_data.get("error")
                or "Request failed"
            )
            raise Exception(f"API error: {error_msg}")
        return CustomerResponse(**response_data)

    def update_customer(self, customer: Customer) -> CustomerResponse:
        request = Request(
            method=HttpMethod.PUT,
            route="v1/admin/aispm/customer",
            data=customer.dict(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return CustomerResponse(**response.json())

    # Cloud Config Methods
    def configure_aws(
        self, configs: List[AWSConfig]
    ) -> List[CloudConfigResponse]:
        request = Request(
            method=HttpMethod.POST,
            route="v1/admin/aispm/config/aws",
            data=[config.dict() for config in configs],
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return [CloudConfigResponse(**config) for config in response.json()]

    def configure_azure(
        self, configs: List[AzureConfig]
    ) -> List[CloudConfigResponse]:
        request = Request(
            method=HttpMethod.POST,
            route="v1/admin/aispm/config/azure",
            data=[config.dict() for config in configs],
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return [CloudConfigResponse(**config) for config in response.json()]

    def get_aws_configs(self) -> Dict:
        """
        Retrieves AWS configurations.
        """
        request = Request(
            method=HttpMethod.GET,
            route="v1/admin/aispm/config/aws",
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return response.json()

    def configure_gcp(
        self, configs: List[GCPConfig]
    ) -> List[CloudConfigResponse]:
        request = Request(
            method=HttpMethod.POST,
            route="v1/admin/aispm/config/gcp",
            data=[config.dict() for config in configs],
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return [CloudConfigResponse(**config) for config in response.json()]

    # Usage Methods
    def get_usage(
        self,
        provider: Optional[str] = None,
        cloud_account: Optional[str] = None,
        model: Optional[str] = None,
        region: Optional[str] = None,
    ) -> UsageResponse:
        route = "v1/admin/aispm/usage"
        if provider:
            route += f"/{provider}"
        if cloud_account:
            route += f"/{cloud_account}"

        params = {}
        if model:
            params["model"] = model
        if region:
            params["region"] = region

        request = Request(
            method=HttpMethod.GET,
            route=route,
            query_params=params,
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return UsageResponse(**response.json())

    # Alert Methods
    def get_alerts(
        self,
        provider: Optional[str] = None,
        cloud_account: Optional[str] = None,
        model: Optional[str] = None,
        region: Optional[str] = None,
    ) -> AlertResponse:
        route = "v1/admin/aispm/alerts"
        if provider:
            route += f"/{provider}"
        if cloud_account:
            route += f"/{cloud_account}"

        params = {}
        if model:
            params["model"] = model
        if region:
            params["region"] = region

        request = Request(
            method=HttpMethod.GET,
            route=route,
            query_params=params,
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return AlertResponse(**response.json())

    # Helpers
    def _validate_provider(self, provider: str) -> None:
        valid_providers = ["aws", "azure", "gcp", "openai"]
        if provider.lower() not in valid_providers:
            raise ValueError(
                f"Invalid provider. Must be one of: {valid_providers}"
            )

    def _construct_error(self, response: Response) -> Dict:
        try:
            error = response.json()
            return error.get("error", str(response.content))
        except json.JSONDecodeError:
            return str(response.content)

    def delete_aws_config(self, name: str) -> None:
        """
        Deletes an AWS configuration by name.

        Args:
            name (str): The name of the AWS configuration to delete

        Raises:
            Exception: If the API request fails
        """
        request = Request(
            method=HttpMethod.DELETE,
            route=f"v1/admin/aispm/config/aws/{name}",
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)

    def get_azure_config(self) -> Dict:
        """
        Retrieves Azure configurations.

        Returns:
            Dict: The Azure configuration data

        Raises:
            Exception: If the API request fails
        """
        request = Request(
            method=HttpMethod.GET,
            route="v1/admin/aispm/config/azure",
            headers=self._get_aispm_headers(),
        )
        response = self.client._send_request_sync(request)
        self._handle_response(response)
        return response.json()
