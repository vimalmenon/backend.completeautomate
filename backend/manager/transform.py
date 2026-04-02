from backend.database import PromptDB

IS_READY = False


def transform_data() -> bool:
    update_prompt()
    return False


def update_prompt():
    if IS_READY:
        prompts = PromptDB().get_all_prompts()
        for prompt in prompts:
            PromptDB().update_prompt(prompt.task, values={"prompt": prompt.prompt})
