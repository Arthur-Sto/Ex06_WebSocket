import asyncio
import websockets
import json

clientes = set()
desenhista_atual = None 

async def servidor(websocket):
    global desenhista_atual 
    
    clientes.add(websocket)

    if desenhista_atual is None:
        desenhista_atual = websocket 
        await websocket.send(json.dumps({"tipo": "sistema", "pode_desenhar": True}))
    else:
        await websocket.send(json.dumps({"tipo": "sistema", "pode_desenhar": False}))

    try:
        async for mensagem in websocket:
            dados = json.loads(mensagem)

            if dados["tipo"] == "chat":
                print(f"Mensagem de chat recebida: {dados['texto']}")
                
                for cliente in clientes:
                    await cliente.send(mensagem)
                    
            elif dados["tipo"] == "desenho":
                if websocket == desenhista_atual:
                    print("Atualização no desenho sendo repassada...")
                    for cliente in clientes:
                        if cliente != websocket: 
                            await cliente.send(mensagem)
                else:
                    print("Aviso: Alguém tentou desenhar fora da vez!")

            elif dados["tipo"] == "passar_vez":
                
                if websocket == desenhista_atual:
                    
                    await websocket.send(json.dumps({"tipo": "sistema", "pode_desenhar": False}))
                    outros_clientes = [c for c in clientes if c != websocket]
                    
                    if len(outros_clientes) > 0:
                        desenhista_atual = outros_clientes[0] 
                        await desenhista_atual.send(json.dumps({"tipo": "sistema", "pode_desenhar": True}))
                        print("A caneta foi passada para outro jogador.")
                    else:
                        desenhista_atual = None
                        print("Ninguém mais na sala. A caneta está livre.")
    finally:
        clientes.remove(websocket)
        
        if websocket == desenhista_atual:
            desenhista_atual = None
            print("O desenhista saiu. A caneta está livre.")

async def main():
    async with websockets.serve(servidor, "localhost", 8080):
        print("Servidor WebSocket iniciado na porta 8080")
        await asyncio.Future()

asyncio.run(main())