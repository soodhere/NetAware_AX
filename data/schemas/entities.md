# Cadence 0 entity shapes (documentation schemas). Runtime uses YAML + Python loaders.

Domain: { id, label, description }
UseCase: { id, label, domainId, existingApis[], networkComplement }
Intent: { id, label, description, defaultPurposeId, exampleRequest }
Purpose: { id, label, description, permittedCapabilityFamilies[] }
Capability: { id, label, family, description }
API / Operation: parsed from pinned OpenAPI — never invented
Enterprise: { id, label, domainId, fictional }
Application: { id, label, enterpriseId, kind }
Agent: { id, label, actsOnBehalfOf, allowedIntents[], identityModel }
Policy: { id, enterpriseId, applicationId, agentId, intentId, purposeId, agreementId }
PolicyRule: { id, policyId, dimension, operator, value }
ConsentRule: { id, policyId, capabilityId, required, available }
Agreement: { id, enterpriseId, kind, permittedPurposes[], permittedRegions[], dataResidency }
AutonomyRule: { id, agentId, intentId, action, level }
Subscription: { id, enterpriseId, capabilityFamily|capabilityId, status }
Entitlement: { id, subscriptionId, applicationId, agentId, scope }
Provider: { id, label, kind, simulated }
Route: { id, type, operationId?, source?, providerId?, domainApi? }

Placeholders only: RuntimeContext, Evidence, Plan, PlanStep, Decision, Invocation, Outcome
