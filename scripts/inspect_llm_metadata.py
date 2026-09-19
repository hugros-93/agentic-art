import asyncio

from langchain_core.messages import HumanMessage

from painting_agents.models.ollama import create_ollama_model


async def main() -> None:
    model = create_ollama_model()

    response = await model.ainvoke(
        [
            HumanMessage(
                content="Reply with exactly: telemetry test"
            )
        ]
    )

    print("\n=== RESPONSE TYPE ===")
    print(type(response))

    print("\n=== RESPONSE ===")
    print(response)

    print("\n=== RESPONSE DICT ===")
    print(response.model_dump())

    print("\n=== RESPONSE METADATA ===")
    print(response.response_metadata)

    print("\n=== USAGE METADATA ===")
    print(response.usage_metadata)


if __name__ == "__main__":
    asyncio.run(main())