from fastapi import FastAPI, HTTPException
from app.services.pathfinder import PathfinderService

app = FastAPI()
pathfinder = PathfinderService()

@app.post("/calculate-path")
async def calculate_path(map_data: dict, start_node: str, end_node: str):
    # 1. Строим граф из полученных данных
    pathfinder.build_graph(map_data)
    
    # 2. Ищем путь
    result = pathfinder.find_path(start_node, end_node)
    
    if not result:
        raise HTTPException(status_code=404, detail="Path not found")
        
    return result