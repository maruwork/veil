# framework selection guide

この guide は
`project-progression-rule.md`
のうち、主に

- `何の入口から読むか`
- `今やる 1 手に対してどの考え方を使うか`

を、補助的な選択面で支える文書である。

この guide の役割は `どの framework family を選ぶか` までである。
選んだ framework 自体の中身、実行順、handoff 契約、証跡化は各 framework 正本側で扱う。

- PS 系 framework の全体像と開始点は
  `ps-suite-guide.md`
- prompt / instruction 改善の反復サイクルは
  `prompt-quality-improvement-cycle.md`

を正本として参照する。

## Purpose

This guide helps a reader choose the right reasoning or prompting framework from the situation they are in.

It is meant to turn framework choice from a pull-style lookup into a push-style classification step:

- first classify the situation
- then select the framework family
- then expand the actual prompt or workflow

## Situation Type Mapping

| Situation type | Typical use | Recommended framework |
|---|---|---|
| Discovery | finding missing pieces, root causes, gaps, hidden problems | CRISP + Cognitive Verifier |
| Comparison | choosing among multiple options, tools, or architectures | Tree of Thoughts + Cognitive Verifier |
| Design | defining instructions, prompts, system behavior, contracts | RISEN |
| Periodic review | measuring current state, direction checks, milestone review | PSM |
| Research | checking latest information, trends, or external updates | CRISP (Q1-Q3) |
| Implementation | asking an agent to write code or produce implementation output | RISEN + CoT |
| Evaluation | checking quality, completeness, or output fitness | CRISP + ReAct |

## How To Use

1. Describe what you want to do.
2. Classify it into one of the situation types above.
3. Pick the corresponding framework.
4. Expand the actual question, prompt, or workflow using that framework.

If a project uses local names or local wrappers around these frameworks, map the local names after classification. The classification step itself should stay portable.

## Output Contract

最低限、次を残す。

- selected_framework_family
- selected_framework
- selection_reason
- rejected_alternatives
- next_expansion_target

## Meta Prompt

```text
I am trying to do "{what I want to do or understand}".

First classify this into one of the following situation types:
A. Discovery (find what is missing or what is wrong)
B. Comparison (choose the best option among multiple options)
C. Design (decide how to build or instruct)
D. Periodic review (measure the current state and decide direction)
E. Research (learn recent information or technical trends)
F. Implementation (ask for code or implementation output)
G. Evaluation (measure quality, completeness, or fitness)

After classifying it, choose the matching framework and then structure the request with that framework before answering.
```

<a id="ui-framework-selection-baseline"></a>
## UI Framework Selection Baseline

UI family を選ぶ時は、少なくとも次を先に答える。

1. prototype / operator dashboard / embedded product UI / standalone chat product のどれか
2. Python-first speed / React customization / no-code flow editing / local-LLM hosting のどれを優先するか
3. 主価値が simple interaction / workflow orchestration / model comparison / in-app task assistance のどれか
4. deployment が local-only / self-hosted web / product-embedded のどれか

使い分けの目安:

- Python だけで最速に形を出したい
  - Streamlit
- visual workflow orchestration を優先したい
  - Dify / Flowise
- 既存 React surface に AI を埋め込みたい
  - assistant-ui / CopilotKit
- standalone chat console を作りたい
  - Lobe Chat
- local model first で self-host したい
  - Open WebUI / Text Generation WebUI

UI family を選んだ場合は、上の output contract に加えて

- selected UI family
- prototype-only か long-term operation 前提か

を残す。
