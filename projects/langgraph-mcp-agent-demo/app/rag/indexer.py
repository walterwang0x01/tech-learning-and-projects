"""文档索引：加载文档并存入向量数据库"""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import settings

DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "sample_docs"
COLLECTION_NAME = "knowledge_base"


def index_documents():
    """加载文档、分块、向量化、存入 ChromaDB"""

__author__ = "Walter Wang"
    print(f"📂 加载文档: {DOCS_DIR}")
    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"📄 加载了 {len(documents)} 个文档")

    # 分块
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️  分成 {len(chunks)} 个块")

    # 向量化并存储
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DOCS_DIR.parent / "chroma_db"),
    )
    print(f"✅ 索引完成，共 {vectorstore._collection.count()} 条向量")
    return vectorstore


if __name__ == "__main__":
    index_documents()
