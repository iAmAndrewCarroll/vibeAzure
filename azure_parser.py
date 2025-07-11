"""
Azure resource parsing utilities
"""
import re
from typing import Dict, Optional, Tuple

class AzureResourceParser:
    """Parse Azure resource IDs and generate portal URLs"""
    
    # Common Azure resource types and their portal paths
    RESOURCE_TYPES = {
        'Microsoft.Compute/virtualMachines': 'virtualMachines',
        'Microsoft.Storage/storageAccounts': 'storageAccounts',
        'Microsoft.Web/sites': 'webApps',
        'Microsoft.Sql/servers': 'sqlServers',
        'Microsoft.KeyVault/vaults': 'vaults',
        'Microsoft.Network/virtualNetworks': 'virtualNetworks',
        'Microsoft.Network/publicIPAddresses': 'publicIPAddresses',
        'Microsoft.Network/networkSecurityGroups': 'networkSecurityGroups',
        'Microsoft.ContainerService/managedClusters': 'managedClusters',
        'Microsoft.CognitiveServices/accounts': 'cognitiveServices',
    }
    
    @staticmethod
    def parse_resource_id(resource_id: str) -> Optional[Dict[str, str]]:
        """Parse an Azure resource ID into components"""
        try:
            # Standard Azure resource ID format:
            # /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{provider}/{resource-type}/{resource-name}
            pattern = r'/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/([^/]+)/([^/]+)/([^/]+)(?:/.*)?'
            match = re.match(pattern, resource_id)
            
            if not match:
                return None
            
            subscription_id, resource_group, provider, resource_type, resource_name = match.groups()
            
            return {
                'subscription_id': subscription_id,
                'resource_group': resource_group,
                'provider': provider,
                'resource_type': resource_type,
                'resource_name': resource_name,
                'full_type': f"{provider}/{resource_type}"
            }
        except Exception:
            return None
    
    @staticmethod
    def get_resource_display_name(resource_id: str) -> str:
        """Get a human-readable name for the resource"""
        parsed = AzureResourceParser.parse_resource_id(resource_id)
        if parsed:
            return f"{parsed['resource_name']} ({parsed['resource_type']})"
        else:
            # Fallback to last part of resource ID
            return resource_id.split('/')[-1]
    
    @staticmethod
    def make_portal_url(resource_id: str) -> Optional[str]:
        """Generate Azure Portal URL for a resource"""
        parsed = AzureResourceParser.parse_resource_id(resource_id)
        if not parsed:
            return None
        
        base_url = "https://portal.azure.com"
        resource_path = f"/subscriptions/{parsed['subscription_id']}/resourceGroups/{parsed['resource_group']}/providers/{parsed['provider']}/{parsed['resource_type']}/{parsed['resource_name']}"
        
        return f"{base_url}/#@/resource{resource_path}"
    
    @staticmethod
    def get_cost_category(resource_id: str) -> str:
        """Categorize resource for cost analysis"""
        parsed = AzureResourceParser.parse_resource_id(resource_id)
        if not parsed:
            return "Other"
        
        full_type = parsed['full_type']
        
        if 'Compute' in full_type:
            return "Compute"
        elif 'Storage' in full_type:
            return "Storage"
        elif 'Network' in full_type:
            return "Networking"
        elif 'Web' in full_type:
            return "Web Apps"
        elif 'Sql' in full_type:
            return "Database"
        elif 'CognitiveServices' in full_type:
            return "AI Services"
        else:
            return "Other"
