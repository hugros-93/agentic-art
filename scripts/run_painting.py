import argparse
import asyncio
from pathlib import Path

from painting_agents.application import create_painting


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a painting using the multi-agent painting system."
    )

    parser.add_argument(
        "request",
        help="Description of the painting to create.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/painting.png"),
        help="Path for the generated PNG.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Maximum Artist/Critic iterations.",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]

    server_script = (
        project_root
        / "scripts"
        / "run_mcp_server.py"
    )

    result = asyncio.run(
        create_painting(
            args.request,
            server_script=server_script,
            output_path=args.output,
            max_iterations=args.max_iterations,
        )
    )

    critique = result.get("critique")

    print(f"\nPainting written to: {args.output}")

    if critique is not None:
        print(f"Approved: {critique.approved}")
        print(f"Assessment: {critique.assessment}")


if __name__ == "__main__":
    main()