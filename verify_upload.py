import asyncio
import json
import websockets

async def check_specific_files():
    print('Checking for files reported as uploaded...\n')
    
    # Files from your log that showed as uploaded
    check_files = [
        'Backwards Mario World.smc',
        'Beachside Blitz.smc',
        'Beautiful (not So) Dangerous.smc',
        'Beto Universe.smc',
        'Brutal Bunny.smc',
        'Candy Shop - Light Edition.smc',
        'Kaizo Kidz.smc',
        'Cute Kaizo World.smc',
        'Ez Kaizo.smc',
        'Jish.smc'
    ]
    
    ws = await websockets.connect('ws://localhost:23074')
    
    await ws.send(json.dumps({'Opcode': 'DeviceList', 'Space': 'SNES'}))
    response = json.loads(await ws.recv())
    device = response['Results'][0]
    
    await ws.send(json.dumps({'Opcode': 'Attach', 'Space': 'SNES', 'Operands': [device]}))
    await asyncio.sleep(1)
    
    # Get all files in the directory
    await ws.send(json.dumps({'Opcode': 'List', 'Space': 'SNES', 'Operands': ['/roms2/Kaizo/01 - Beginner']}))
    response = await asyncio.wait_for(ws.recv(), timeout=10)
    data = json.loads(response)
    
    sd_files = []
    if 'Results' in data:
        results = data['Results']
        for i in range(0, len(results), 2):
            if i + 1 < len(results):
                if results[i] == '1' and results[i+1] not in ['.', '..']:
                    sd_files.append(results[i+1])
    
    print(f'Total files on SD in /roms2/Kaizo/01 - Beginner: {len(sd_files)}\n')
    
    print('Checking specific files:')
    found_count = 0
    for check_file in check_files:
        if check_file in sd_files:
            print(f'   FOUND: {check_file}')
            found_count += 1
        else:
            print(f'   MISSING: {check_file}')
    
    print(f'\nResult: {found_count}/{len(check_files)} files verified on SD card')
    
    if found_count == 0:
        print('\nWARNING: NO files found! The uploads may have failed.')
        print('The fire-and-forget protocol may need longer delays.')
    elif found_count < len(check_files):
        print(f'\nWARNING: Only {found_count}/{len(check_files)} files verified.')
        print('Some uploads may still be processing.')
    else:
        print('\nSUCCESS: All checked files are on the SD card!')
    
    await ws.close()

asyncio.run(check_specific_files())
