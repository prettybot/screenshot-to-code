from typing import Awaitable, Callable, List
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk

MODEL_GPT_4_VISION = "gpt-4-vision-preview"


async def stream_openai_response(
    messages: List[ChatCompletionMessageParam],
    azure_openai_api_key: str,
    azure_openai_resource_name: str | None,
    azure_openai_deployment_name: str | None,
    callback: Callable[[str], Awaitable[None]],
) -> str:
    client = AsyncAzureOpenAI(
        api_version="2023-12-01-preview",
        api_key=azure_openai_api_key,
        azure_endpoint=f"https://{azure_openai_resource_name}.openai.azure.com/",
        azure_deployment=azure_openai_deployment_name
)

    model = MODEL_GPT_4_VISION

    # Base parameters
    params = {"model": model, "messages": messages, "stream": True, "timeout": 600}

    # Add 'max_tokens' only if the model is a GPT4 vision model
    if model == MODEL_GPT_4_VISION:
        params["max_tokens"] = 4096
        params["temperature"] = 0

    stream = await client.chat.completions.create(**params)  # type: ignore
    full_response = ""
    async for chunk in stream:  # type: ignore
        assert isinstance(chunk, ChatCompletionChunk)
        content = chunk.choices[0].delta.content or ""
        full_response += content
        await callback(content)

    await client.close()

    return full_response
