# Experiment Protocol Template (minimal controlled experiment)

> Purpose: validate "is this way of collaborating worth it" on a small sample before investing heavily.
> Usage: copy this file, replace {{placeholders}}.

## Experiment info
- ID: {{EXP-XXX}}
- Date: {{YYYY-MM-DD}}
- Question: {{collab vs solo? select-best vs merge? team size?}}

## Standard task (identical for both groups!)
> {{task description. Must be repeatable and measurable. e.g., "write a ≤200-word positioning statement" or "implement function f"}}

## Group design
| Group | Mode | Execution |
|---|---|---|
| A | Solo | {{1 agent direct output}} |
| B | Collaboration | {{N roles each draft → integrate / select-best}} |

## Metrics (objective first)
| Dimension | Description | Scale |
|---|---|---|
| {{functional tests}} | {{passing cases}} | 0-n |
| {{quality dimensions}} | {{readability etc.}} | 1-5 |
| {{process cost}} | {{agents × rounds}} | record |

## Conclusion template
- Quality: A=__ vs B=__
- Cost: A=__ vs B=__
- Recommendation: {{is collaboration worth it / how to handle drafts}}

---
💡 Three evidence-based rules:
1. Collaboration value ∝ task openness × complexity (low=0%, mid=+7%, high=+19%)
2. Select-best saturates at 3 roles; more roles add coverage only
3. Default to select-best; merge only to combine substantive elements
