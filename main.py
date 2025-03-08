
import asyncio
import game.main  # サブディレクトリのメインゲームロジック

async def main():
    # サブ側の async_main を呼び出すだけ
    await game.main.async_main()

if __name__ == "__main__":
    asyncio.run(main())
