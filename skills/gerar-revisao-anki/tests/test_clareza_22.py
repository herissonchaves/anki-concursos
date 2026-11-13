from pathlib import Path
import importlib.util
path=Path(__file__).resolve().parents[1]/'scripts'/'auditar_clareza.py'
spec=importlib.util.spec_from_file_location('clarity22',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def signals(front,back='Explicação sintética suficientemente longa para este teste de sinais.'):
    return {x['sinal'] for x in m.scan([{'id':'TEST','tipo':'cloze','front':front,'back':back,'tags':''}])}

def test_visible_answer_and_other_view():
    assert 'RESPOSTA_CLOZE_VISIVEL' in signals('Uma resposta {{c1::absoluta}} é absoluta.')
    assert 'RESPOSTA_CLOZE_VISIVEL' in signals('{{c1::conceito}} e {{c2::conceito}}')
    assert 'RESPOSTA_CLOZE_VISIVEL' not in signals('O alvo é {{c1::conceito}}.')
    assert 'RESPOSTA_CLOZE_VISIVEL' not in signals('{{c1::conceito}} e {{c1::conceito}}')

def test_mnemonic_remote_and_presumed_success():
    assert 'MEMORIA_DE_SIGLA' in signals('A letra X da sigla significa {{c1::exemplo}}.')
    assert 'MIDIA_REMOTA' in signals('<img src="https://example.org/image.png"> {{c1::alvo}}')
    assert 'ACERTO_PRESUMIDO' in signals('{{c1::alvo}}','Você acertou! Esta frase é apenas uma fixture sintética de teste.')
