#!/usr/bin/env bash
set -euo pipefail

cd /Users/zhaoruicn/.openclaw/workspace
GROUP="${1:-all}"
CURRENT_MODEL="${CURRENT_MODEL:-Feinian / GPT-5.4}"
TODAY="$(date +%F)"

refresh_execution() {
  python3 scripts/execution_center_card.py >/dev/null
  python3 scripts/runtime_tasks_panel_card.py >/dev/null
  python3 scripts/semantic_execution_panel_card.py >/dev/null
  python3 scripts/screen_detail_panel_card.py >/dev/null
  python3 scripts/acp_semantic_panel_card.py >/dev/null
  python3 scripts/acp_detail_panel_card.py >/dev/null
  python3 scripts/task_history_panel_card.py >/dev/null
  python3 scripts/rerun_test_tasks_panel_card.py >/dev/null
  python3 scripts/clean_test_tasks_panel_card.py >/dev/null
}

refresh_tasks() {
  python3 scripts/focus_panel_card.py >/dev/null
  python3 scripts/task_panel_card.py >/dev/null
  python3 scripts/memory_panel_card.py >/dev/null
  python3 scripts/workspace_dashboard_card.py generate --day "$TODAY" >/dev/null || true
}

refresh_system() {
  python3 scripts/system_panel_card.py >/dev/null
  python3 scripts/scheduled_tasks_panel_card.py >/dev/null
}

refresh_models() {
  python3 scripts/model_panel_card.py >/dev/null
  python3 scripts/openclaw_model_card.py >/dev/null
  python3 scripts/cc_model_card.py >/dev/null
  CURRENT_MODEL="$CURRENT_MODEL" python3 scripts/cockpit_v6_hub.py --current-model "$CURRENT_MODEL" >/dev/null
}

refresh_navigation() {
  python3 scripts/quick_actions_panel_card.py >/dev/null
  python3 scripts/light_control_panel_card.py >/dev/null
  python3 scripts/cockpit_v5.py --sub execution_hub >/dev/null
  python3 scripts/cockpit_v5.py --sub task_hub >/dev/null
  python3 scripts/cockpit_v5.py --sub system_hub >/dev/null
  python3 scripts/cockpit_v5.py --sub model_control_hub >/dev/null
  python3 scripts/cockpit_v5.py --sub quick_hub >/dev/null
}

case "$GROUP" in
  execution)
    refresh_execution
    ;;
  tasks)
    refresh_tasks
    ;;
  system)
    refresh_system
    ;;
  models)
    refresh_models
    ;;
  nav|navigation)
    refresh_navigation
    ;;
  all)
    refresh_execution
    refresh_tasks
    refresh_system
    refresh_models
    refresh_navigation
    ;;
  *)
    echo "Usage: $0 [all|execution|tasks|system|models|nav]" >&2
    exit 1
    ;;
esac

echo "✅ refreshed group=$GROUP"
