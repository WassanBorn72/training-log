import json
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':360,'height':800})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.route('http://gymlog.test/**',lambda route: route.fulfill(body=Path('www/index.html').read_text(),content_type='text/html'))
    state={'exercises':[{'id':'bench','name':'ベンチプレス','part':'胸','notes':'シート 4'}], 'history':[{'id':'old','date':'2026-10-01','exercises':[{'exerciseId':'bench','name':'旧種目名','part':'胸','sets':[{'weight':'50','unit':'kg','reps':'8'}]}]}], 'templates':[], 'drafts':{}}
    page.add_init_script('if(!localStorage.getItem("ironlog-v1"))localStorage.setItem("ironlog-v1",'+json.dumps(json.dumps(state))+')')
    page.goto('http://gymlog.test/')
    page.locator('#add').click()
    page.locator('[data-pick="bench"]').click()
    assert page.locator('[data-note]').input_value()=='シート 4'
    page.locator('[data-note]').fill('シート 5\n背もたれ 2')
    page.locator('#dateLabel').click()
    assert json.loads(page.evaluate('localStorage.getItem("ironlog-v1")'))['exercises'][0]['notes']=='シート 5\n背もたれ 2'
    page.reload()
    assert page.locator('[data-note]').input_value()=='シート 5\n背もたれ 2'
    page.locator('[data-tab="history"]').click()
    assert '2026-10-01' in page.locator('#histList').inner_text()
    page.locator('#historyExercise').click()
    assert 'ベンチプレス' in page.locator('#historyExerciseSelect').inner_text()
    assert '50 kg × 8 回' in page.locator('#histList').inner_text()
    page.locator('#search').fill('nothing')
    assert '一致する記録がありません' in page.locator('#histList').inner_text()
    page.locator('#search').fill('')
    page.locator('#historyDate').click()
    assert page.locator('[data-hist="old"]').count()==1
    page.locator('#start').click()
    assert '一時停止' in page.locator('#start').inner_text()
    page.locator('#start').click()
    assert '再開' in page.locator('#start').inner_text()
    page.locator('#timerSettings summary').click()
    page.locator('[data-time="30"]').click()
    assert page.locator('#clock').inner_text()=='00:30'
    for width in [320,360,412]:
        page.set_viewport_size({'width':width,'height':800})
        page.evaluate('document.documentElement.style.setProperty("--safe-area-inset-bottom","24px")')
        page.wait_for_timeout(100)
        dock=page.locator('.timer-dock').bounding_box();nav=page.locator('nav').bounding_box()
        assert dock['y']+dock['height'] <= nav['y'],(dock,nav)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('#timerSettings summary').click()
    page.locator('[data-tab="work"]').click()
    page.locator('#save').scroll_into_view_if_needed()
    page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
    page.wait_for_timeout(100)
    save=page.locator('#save').bounding_box();dock=page.locator('.timer-dock').bounding_box()
    assert save['y']+save['height']<=dock['y']
    page.screenshot(path='/workspace/training-log/preview.png',full_page=True)
    assert not errors,errors
    # Older backups without drafts remain usable.
    page.locator('[data-tab="settings"]').click()
    page.on('dialog',lambda dialog: dialog.accept())
    backup=dict(state);backup.pop('drafts')
    page.locator('#file').set_input_files({'name':'old.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
    page.wait_for_timeout(200)
    assert not errors,errors
    assert 'drafts' in json.loads(page.evaluate('localStorage.getItem("ironlog-v1")'))
    browser.close()
print('PASS: legacy data, notes persistence, history modes, timer controls, safe area at 320/360/412px, save button clearance, older backup restore')
