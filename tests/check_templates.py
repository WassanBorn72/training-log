"""Regression checks for template context, legacy data and narrow-screen controls."""
import copy
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

KEY = 'ironlog-v1'
BENCH = {'id': 'bench', 'name': 'ベンチプレス', 'part': '胸', 'notes': 'シート 4'}
ROW = {'id': 'row', 'name': 'シーテッドロー', 'part': '背中', 'notes': ''}


def entry(weight='80', unit='kg', reps='10', name='ベンチプレス', exercise_id='bench'):
    return {'id': 'entry', 'exerciseId': exercise_id, 'name': name, 'part': '胸',
            'sets': [{'weight': weight, 'unit': unit, 'reps': reps}]}


def session(day, weight, template=None, **kwargs):
    record = {'id': day, 'date': day, 'exercises': [entry(weight, **kwargs)]}
    if template:
        record.update(templateId=template, templateName='同じ名前のメニュー')
    return record


seed = {
    'exercises': [BENCH, ROW],
    # Both templates have the same name, and legacy templates contain sets.
    'templates': [{'id': name, 'name': '同じ名前のメニュー', 'exercises': [entry()]}
                  for name in ['A', 'B', 'new']],
    'history': [session('2026-10-01', '20', 'A', unit='lbs', reps='8', name='旧種目名'),
                session('2026-10-10', '30', 'B'), session('2026-10-20', '40')],
    'drafts': {'2026-11-02': [entry('99')]},
}


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 360, 'height': 800}, accept_downloads=True)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.accept())
    page.route('http://gymlog.test/**', lambda route: route.fulfill(
        body=Path('www/index.html').read_text(), content_type='text/html'))
    page.goto('http://gymlog.test/')

    def stored():
        return page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)

    def install(data):
        page.evaluate('([key,data]) => localStorage.setItem(key,JSON.stringify(data))', [KEY, data])
        page.reload()
        page.locator('#date').fill('2026-11-02')
        page.locator('#date').dispatch_event('change')

    def tab(name):
        page.locator(f'[data-tab="{name}"]').click()

    def load(template):
        tab('settings')
        page.locator(f'[data-load="{template}"]').click()

    def previous():
        page.locator('[data-copy-prev="0"]').click()

    def value(field):
        return page.locator(f'[data-e="0"][data-s="0"][data-k="{field}"]').input_value()

    install(seed)
    # Saving captures only exercise identities/order, with no entry IDs or sets.
    tab('settings')
    page.locator('#templateName').fill('新しいメニュー')
    page.locator('#saveTemplate').click()
    saved = stored()['templates'][-1]
    assert saved['exercises'] == [{'exerciseId': 'bench', 'name': 'ベンチプレス', 'part': '胸'}]
    load(saved['id'])
    assert value('weight') == '' and value('reps') == ''
    assert page.locator('.set').count() == 3
    previous()
    assert value('weight') == ''  # Never fall back to a different menu.

    # An old template with stored numbers also loads with fresh empty sets.
    load('A')
    assert value('weight') == '' and value('reps') == '' and value('unit') == 'kg'
    previous()
    assert (value('weight'), value('unit'), value('reps')) == ('20', 'lbs', '8')
    assert page.locator('.set').count() == 1
    assert '同じ名前のメニュー' in page.locator('#templateContext').inner_text()
    assert stored()['history'] == seed['history']
    # Menu context survives reload/date switching.
    page.reload()
    page.locator('#date').fill('2026-11-02')
    page.locator('#date').dispatch_event('change')
    assert not page.locator('#templateContext').is_hidden()
    page.locator('#date').fill('2026-11-03')
    page.locator('#date').dispatch_event('change')
    assert '種目ごとの前回' in page.locator('#templateContext').inner_text()
    page.locator('#date').fill('2026-11-02')
    page.locator('#date').dispatch_event('change')
    assert not page.locator('#templateContext').is_hidden()
    assert page.locator('[data-copy-ex]').count() == 0  # One unambiguous copy action.
    load('B')
    previous()
    assert value('weight') == '30'  # Same name does not mean same template.
    load('new')
    previous()
    assert value('weight') == ''

    load('A')
    page.locator('[data-k="weight"]').first.fill('25')
    page.locator('[data-k="weight"]').first.dispatch_event('change')
    page.locator('#save').click()
    assert stored()['history'][-1]['templateId'] == 'A'
    page.locator('#date').fill('2026-11-03')
    page.locator('#date').dispatch_event('change')
    load('A')
    previous()
    assert value('weight') == '25'
    assert value('reps') == ''  # Blank saved values are preserved.

    # Backup and restore preserve menu associations and legacy records.
    tab('settings')
    with page.expect_download() as download_info:
        page.locator('#export').click()
    exported = json.loads(Path(download_info.value.path()).read_text())
    assert exported['state']['draftTemplates']['2026-11-03']['id'] == 'A'
    page.locator('#file').set_input_files({'name': 'backup.json', 'mimeType': 'application/json',
                                         'buffer': json.dumps(exported).encode()})
    page.wait_for_timeout(100)
    assert stored()['history'] == exported['state']['history']

    # Latest use of a menu lacked this exercise: do not retrieve an older use.
    missing = copy.deepcopy(seed)
    missing['history'].append({'id': 'last-A', 'date': '2026-10-25', 'templateId': 'A',
                               'exercises': [entry('55', name='シーテッドロー', exercise_id='row')]})
    install(missing)
    load('A')
    previous()
    assert value('weight') == ''

    # Unknown legacy history isn't assigned to a menu by matching its exercises.
    old = copy.deepcopy(seed)
    old['history'] = [session('2026-10-20', '70')]
    install(old)
    page.locator('[data-copy-prev="0"]').click()
    assert value('weight') == '70'
    load('A')
    previous()
    assert value('weight') == ''

    # Unit controls remain fixed-width and actions don't split their text.
    for width in [320, 360, 412]:
        page.set_viewport_size({'width': width, 'height': 800})
        page.evaluate('document.documentElement.style.setProperty("--safe-area-inset-bottom","24px")')
        for unit in ['kg', 'lbs']:
            page.locator('[data-k="unit"]').first.select_option(unit)
            assert value('unit') == unit
            unit_box = page.locator('[data-k="unit"]').first.bounding_box()
            assert unit_box['width'] >= 64
        for selector in ['[data-add-set="0"]', '[data-copy-prev="0"]']:
            assert page.locator(selector).evaluate('el => getComputedStyle(el).whiteSpace') == 'nowrap'
            assert page.locator(selector).evaluate('el => el.scrollWidth <= el.clientWidth')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#save').scroll_into_view_if_needed()
        page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
        page.wait_for_timeout(100)
        save, dock = page.locator('#save').bounding_box(), page.locator('.timer-dock').bounding_box()
        assert save['y'] + save['height'] <= dock['y']
        page.screenshot(path=f'/tmp/gymlog-menu-{width}.png', full_page=True)
    assert not errors, errors
    browser.close()
print('PASS: exercise-only templates, menu-specific copy, legacy data, draft context, backup/restore, compact layout')
