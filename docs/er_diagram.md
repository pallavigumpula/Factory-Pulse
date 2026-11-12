# FactoryPulse — Entity-Relationship Diagram (ERD)

This document visualizes the complete normalized relational schema for **FactoryPulse**, representing plant hierarchies, production execution, machine states, quality inspections, downtime tracking, and OEE aggregation.

```mermaid
erDiagram
    users ||--o{ production_counts : "logs"
    users ||--o{ quality_inspections : "inspects"
    
    plants ||--o{ production_lines : "contains"
    plants ||--o{ shifts : "operates"
    
    production_lines ||--o{ machines : "houses"
    production_lines ||--o{ production_orders : "executes"
    
    machines ||--o{ machine_state_events : "generates"
    machines ||--o{ production_counts : "produces"
    machines ||--o{ quality_inspections : "inspected_at"
    
    shifts ||--o{ machine_state_events : "occurs_during"
    shifts ||--o{ production_counts : "recorded_during"
    shifts ||--o{ quality_inspections : "tested_during"
    
    products ||--o{ production_orders : "scheduled_for"
    products ||--o{ production_counts : "counted_as"
    
    production_orders ||--o{ machine_state_events : "context_for"
    production_orders ||--o{ production_counts : "accumulates"
    production_orders ||--o{ quality_inspections : "validated_by"
    
    downtime_reasons ||--o{ machine_state_events : "categorizes"
    
    production_counts ||--o{ production_counts : "traces_correction"

    users {
        int id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    plants {
        int id PK
        string plant_code UK
        string name
        string location
        string timezone
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    production_lines {
        int id PK
        int plant_id FK
        string line_code UK
        string name
        decimal target_oee
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    machines {
        int id PK
        int line_id FK
        string machine_code UK
        string name
        string model
        string current_status
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    shifts {
        int id PK
        int plant_id FK
        string shift_code
        string name
        time start_time
        time end_time
        int planned_break_minutes
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    products {
        int id PK
        string product_code UK
        string name
        string category
        decimal ideal_cycle_time_seconds
        string unit_of_measure
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    downtime_reasons {
        int id PK
        string reason_code UK
        string category
        string name
        string description
        boolean is_planned
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    production_orders {
        int id PK
        string order_code UK
        int line_id FK
        int product_id FK
        int target_quantity
        int produced_quantity
        string status
        datetime start_time
        datetime end_time
        datetime created_at
        datetime updated_at
    }

    machine_state_events {
        int id PK
        string event_code UK
        int machine_id FK
        int production_order_id FK
        int shift_id FK
        string state
        datetime start_time
        datetime end_time
        int duration_seconds
        int downtime_reason_id FK
        string notes
        datetime created_at
        datetime updated_at
    }

    production_counts {
        int id PK
        string count_code UK
        int production_order_id FK
        int machine_id FK
        int shift_id FK
        int product_id FK
        string count_type
        int quantity
        datetime timestamp
        int operator_id FK
        int reference_count_id FK
        string reason
        datetime created_at
        datetime updated_at
    }

    quality_inspections {
        int id PK
        string inspection_code UK
        int production_order_id FK
        int machine_id FK
        int shift_id FK
        int sample_size
        int passed_count
        int failed_count
        string defect_type
        int inspector_id FK
        datetime timestamp
        string status
        string notes
        datetime created_at
        datetime updated_at
    }

    oee_aggregates {
        int id PK
        string aggregation_level
        int entity_id
        string entity_code
        date date
        int shift_id
        decimal planned_production_time_minutes
        decimal operating_time_minutes
        decimal planned_downtime_minutes
        decimal unplanned_downtime_minutes
        decimal ideal_cycle_time_seconds
        int total_count
        int good_count
        int scrap_count
        int rework_count
        decimal availability
        decimal performance
        decimal quality
        decimal oee
        boolean performance_flagged
        datetime calculated_at
    }

    detected_anomalies {
        int id PK
        string anomaly_code UK
        string anomaly_type
        string entity_type
        string entity_id
        datetime timestamp
        string severity
        string description
        string expected_value
        string actual_value
        string recommended_action
        string resolution_status
        datetime detected_at
        datetime resolved_at
    }
```
