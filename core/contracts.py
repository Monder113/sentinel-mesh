"""
Sentinel Mesh - Smart Contract Engine

This module implements an automated response system that triggers
defensive actions when threats are detected by the AI.

Smart contracts are predefined rules that execute automatically
when certain conditions are met (e.g., anomaly confidence > threshold).
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class ActionType(Enum):
    """Available defensive actions that can be triggered."""
    BLOCK_IP = "BLOCK_IP"           # Block the suspicious source
    RATE_LIMIT = "RATE_LIMIT"       # Limit connection rate
    QUARANTINE = "QUARANTINE"       # Isolate the traffic for analysis
    ALERT_NETWORK = "ALERT_NETWORK" # Broadcast alert to all peers


class TriggerType(Enum):
    """Events that can trigger a contract."""
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"     # MSE > high threshold
    REPEATED_OFFENSE = "REPEATED_OFFENSE"   # Multiple anomalies from same source


@dataclass
class Contract:
    """
    A smart contract definition.
    
    Attributes:
        name: Human-readable contract name
        action: The defensive action to take
        trigger: What event triggers this contract
        threshold: Minimum confidence/MSE to activate (0.0 - 1.0)
        cooldown: Seconds before this contract can trigger again
        enabled: Whether this contract is active
    """
    name: str
    action: ActionType
    trigger: TriggerType
    threshold: float = 0.0
    cooldown: int = 60
    enabled: bool = True
    last_triggered: float = 0.0


@dataclass
class ExecutedAction:
    """Record of an action that was executed."""
    contract_name: str
    action: ActionType
    timestamp: float
    details: dict = field(default_factory=dict)


class ContractEngine:
    """
    The engine that evaluates and executes smart contracts.
    
    This simulates automated threat response - in a real system,
    these actions would interface with firewalls, load balancers, etc.
    """
    
    def __init__(self):
        # Default contracts - can be customized
        self.contracts: List[Contract] = [
            Contract(
                name="Auto-Block High Threat",
                action=ActionType.BLOCK_IP,
                trigger=TriggerType.HIGH_CONFIDENCE,
                threshold=0.15,  # High MSE = likely attack
                cooldown=120
            ),
            Contract(
                name="Rate Limit on Anomaly",
                action=ActionType.RATE_LIMIT,
                trigger=TriggerType.ANOMALY_DETECTED,
                threshold=0.05,
                cooldown=30
            ),
            Contract(
                name="Network Alert Broadcast",
                action=ActionType.ALERT_NETWORK,
                trigger=TriggerType.ANOMALY_DETECTED,
                threshold=0.0,  # Always alert on any anomaly
                cooldown=10
            ),
        ]
        
        # History of executed actions
        self.action_history: List[ExecutedAction] = []
        
        # Simulated blocklist (in real system, this would be firewall rules)
        self.blocked_ips: set = set()
        self.rate_limited: dict = {}  # IP -> limit_until timestamp
    
    def evaluate(self, alert_type: str, confidence: float, source_ip: str = "unknown") -> List[ExecutedAction]:
        """
        Evaluate all contracts against an alert and execute matching ones.
        
        Args:
            alert_type: Type of alert (e.g., "AI_ANOMALY_DETECTED")
            confidence: The MSE/confidence score from AI
            source_ip: Source of the suspicious traffic (simulated)
            
        Returns:
            List of actions that were executed
        """
        executed = []
        current_time = time.time()
        
        for contract in self.contracts:
            if not contract.enabled:
                continue
                
            # Check cooldown
            if current_time - contract.last_triggered < contract.cooldown:
                continue
            
            # Check if trigger matches
            trigger_matched = False
            if contract.trigger == TriggerType.ANOMALY_DETECTED and "ANOMALY" in alert_type:
                trigger_matched = True
            elif contract.trigger == TriggerType.HIGH_CONFIDENCE and confidence > contract.threshold:
                trigger_matched = True
            
            # Execute if conditions met
            if trigger_matched and confidence >= contract.threshold:
                action = self._execute_action(contract, source_ip, confidence)
                contract.last_triggered = current_time
                executed.append(action)
                self.action_history.append(action)
        
        return executed
    
    def _execute_action(self, contract: Contract, source_ip: str, confidence: float) -> ExecutedAction:
        """
        Execute a contract's action (simulated).
        
        In a production system, this would interface with:
        - Firewall APIs (for BLOCK_IP)
        - Load balancer (for RATE_LIMIT)
        - SIEM systems (for ALERT_NETWORK)
        """
        details = {
            "source_ip": source_ip,
            "confidence": round(confidence, 4),
            "simulated": True  # Flag that this is a simulation
        }
        
        if contract.action == ActionType.BLOCK_IP:
            self.blocked_ips.add(source_ip)
            details["message"] = f"IP {source_ip} added to blocklist"
            print(f"CONTRACT EXECUTED: {contract.name} - Blocked {source_ip}")
            
        elif contract.action == ActionType.RATE_LIMIT:
            self.rate_limited[source_ip] = time.time() + 300  # 5 min limit
            details["message"] = f"IP {source_ip} rate limited for 5 minutes"
            print(f"CONTRACT EXECUTED: {contract.name} - Rate limiting {source_ip}")
            
        elif contract.action == ActionType.QUARANTINE:
            details["message"] = f"Traffic from {source_ip} quarantined for analysis"
            print(f"CONTRACT EXECUTED: {contract.name} - Quarantined {source_ip}")
            
        elif contract.action == ActionType.ALERT_NETWORK:
            details["message"] = "Alert broadcasted to all peer nodes"
            print(f"CONTRACT EXECUTED: {contract.name} - Network alert sent")
        
        return ExecutedAction(
            contract_name=contract.name,
            action=contract.action,
            timestamp=time.time(),
            details=details
        )
    
    def get_status(self) -> dict:
        """Return current contract engine status."""
        return {
            "total_contracts": len(self.contracts),
            "enabled_contracts": sum(1 for c in self.contracts if c.enabled),
            "blocked_ips": list(self.blocked_ips),
            "rate_limited_count": len(self.rate_limited),
            "total_actions_executed": len(self.action_history),
            "recent_actions": [
                {
                    "contract": a.contract_name,
                    "action": a.action.value,
                    "time": a.timestamp,
                    "details": a.details
                }
                for a in self.action_history[-5:]  # Last 5 actions
            ]
        }
    
    def get_contracts_info(self) -> List[dict]:
        """Return info about all contracts."""
        return [
            {
                "name": c.name,
                "action": c.action.value,
                "trigger": c.trigger.value,
                "threshold": c.threshold,
                "cooldown": c.cooldown,
                "enabled": c.enabled
            }
            for c in self.contracts
        ]
