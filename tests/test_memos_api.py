import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_create_memo(client):
    payload = {
        "title": "Test Memo",
        "content": "This is a test content",
        "tags": ["test", "qa"],
        "priority": 2
    }
    response = await client.post("/memos/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert "id" in data
    return data

@pytest.mark.asyncio
async def test_create_memo_validation_error(client):
    # Missing content
    payload = {"title": "No Content"}
    response = await client.post("/memos/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_read_memos(client):
    # Create a couple of memos
    await client.post("/memos/", json={"title": "M1", "content": "C1"})
    await client.post("/memos/", json={"title": "M2", "content": "C2"})
    
    response = await client.get("/memos/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_read_memo_by_id(client):
    create_res = await client.post("/memos/", json={"title": "Read Me", "content": "Content"})
    memo_id = create_res.json()["id"]
    
    response = await client.get(f"/memos/{memo_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == memo_id

@pytest.mark.asyncio
async def test_read_memo_not_found(client):
    response = await client.get("/memos/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_memo(client):
    create_res = await client.post("/memos/", json={"title": "Original", "content": "Content"})
    memo_id = create_res.json()["id"]
    
    update_payload = {"title": "Updated Title", "is_favorite": True}
    response = await client.put(f"/memos/{memo_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_favorite"] is True
    # Content should remain unchanged
    assert data["content"] == "Content"

@pytest.mark.asyncio
async def test_update_memo_not_found(client):
    response = await client.put("/memos/99999", json={"title": "Ghost"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_memo(client):
    create_res = await client.post("/memos/", json={"title": "To Delete", "content": "Content"})
    memo_id = create_res.json()["id"]
    
    # Delete
    response = await client.delete(f"/memos/{memo_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it is gone
    get_res = await client.get(f"/memos/{memo_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_memo_not_found(client):
    response = await client.delete("/memos/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_search_memos(client):
    await client.post("/memos/", json={"title": "UniqueKeyword", "content": "Hidden content"})
    await client.post("/memos/", json={"title": "Another", "content": "No match"})
    
    response = await client.get("/memos/search/?q=Unique")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "UniqueKeyword"
