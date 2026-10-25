"""Offline provider readiness. CLI features do not establish wrapper permission."""

AGY_BATCH_BLOCK_REASON = (
    "POLICY_CLARIFICATION_REQUIRED: AGY headless supports direct scripting/CI, "
    "but consumer policy does not clearly permit Course Harness's "
    "Worker/Auditor/Repair application orchestration. No live batch is enabled. "
    "Manual handoff is debugging/fallback only. Gemini API is inactive."
)


def provider_readiness(mode=None, config_path="course_harness/config.yaml"):
    """Return policy facts without running a CLI, checking credentials or spending quota."""
    if mode is None:
        import yaml
        with open(config_path, encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        mode = config.get("execution", {}).get("mode", "automated_cli")
    return {
        "intended_provider": "agy",
        "model_requested": "gemini-3.8-flash-high",
        "effort_requested": "high",
        "execution_mode": mode,
        "status": "POLICY_CLARIFICATION_REQUIRED" if mode == "automated_cli" else (
            "DEBUG_FALLBACK_ONLY" if mode == "manual_cli_handoff" else (
                "OFFLINE_TEST_ONLY" if mode == "mock" else "PROVIDER_DISABLED")),
        "direct_scripting_and_ci": "DOCUMENTED",
        "course_harness_live_batch_supported": False,
        "third_party_agent_or_application_wrapper": "NOT_SUPPORTED_UNDER_CONSUMER_PLANS",
        "manual_handoff": "DEBUG_FALLBACK_ONLY",
        "gemini_api": "INACTIVE_NOT_AUTHORIZED",
        "model_verification": "NOT_CHECKED",
        "authentication": "NOT_CHECKED",
        "quota": "NOT_CHECKED",
        "provider_calls": 0,
        "policy_sources": [
            "https://antigravity.google/docs/cli/headless/",
            "https://antigravity.google/docs/faq",
            "https://antigravity.google/terms",
            "https://discuss.ai.google.dev/t/clarification-on-consumer-plan-policy-for-invoking-official-agy-via-local-subprocess/189905",
        ],
    }
