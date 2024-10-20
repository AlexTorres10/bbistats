from django.shortcuts import render
from django.db import connection
from .models import *
from .bbi_functions import *
from datetime import datetime

def get_results(time):
    return Result.objects.filter(casa=time) | Result.objects.filter(fora=time).order_by('data')

def forma_tabela(divisao, tipo_tabela=''):
    times_da_liga = Time.objects.filter(divisao=divisao).order_by('time')
    colunas_tabela = ['Time','J','V','E','D','GM','GS','SG','Pts']
    tabela = pd.DataFrame(columns=colunas_tabela)

    for time in times_da_liga:
        novo_time = {'Time': time.time, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GM': 0, 'GS': 0, 'SG': 0, 'Pts': 0}
        tabela = pd.concat([tabela, pd.DataFrame([novo_time])], ignore_index=True)

    if tipo_tabela == '':
        times_que_perderam_pts = ['Sheffield United']
        pontos_a_tirar = {'Sheffield United': 2}

        for team in times_que_perderam_pts:
            if team in tabela['Time'].values:
                # Subtract points for the specific team
                tabela.loc[tabela['Time'] == team, 'Pts'] -= pontos_a_tirar.get(team, 0)

    resultados_da_liga = Result.objects.filter(liga=divisao).order_by('data')
    for result in resultados_da_liga:
        atualiza_tabela(tabela, result.casa, result.fora, result.placar, tipo_tabela)
    tabela = tabela.sort_values(by=['Pts','SG','GM'], ascending=False,ignore_index=False).reset_index(drop=True).reset_index()
    tabela['index'] = tabela['index']+1
    tabela = tabela.rename(columns={'index':'Pos'})

    times_da_liga = Time.objects.filter(divisao=divisao).order_by('time')

    df_times = pd.DataFrame.from_records(times_da_liga.values())
    df_times.columns = ['idtimes', 'Time', 'divisao', 'url']
    tabela = tabela.merge(df_times[['Time', 'url']], on='Time',how='left')
    return tabela


# Request permite acessar os dados daquela página
def home(request):
    # request = dados, e a página HTML responsável

    ligas = ['Premier League', 'Championship', 'League One', 'League Two', 'National League']
    tabela_da_liga = {}
    show_tabela = {}
    for l in ligas:
        tabela_da_liga[l] = forma_tabela(l)
        show_tabela[l] = tabela_da_liga[l].head(7)[['Time', 'J', 'SG', 'Pts', 'url']]

    context = {
        'tabelas':{
            'Premier League': show_tabela['Premier League'],
            'Championship': show_tabela['Championship'],
            'League One': show_tabela['League One'],
            'League Two': show_tabela['League Two'],
            'National League': show_tabela['National League'],
        }
    }

    return render(request, 'home.html', context)


def liga(request, liga):
    liga_base = liga.replace('-',' ').title()
    times_da_liga = Time.objects.filter(divisao=liga_base).order_by('time')

    df_times = pd.DataFrame.from_records(times_da_liga.values())
    df_times.columns = ['idtimes', 'time', 'divisao', 'url']

    results ={}
    
    for time in df_times['time'].unique():
        resultados = get_results(time)
        df = pd.DataFrame.from_records(resultados.values())
        try:
            df.columns = ['idresults', 'casa', 'placar', 'fora', 'data', 'liga']
            df['result'] = df.apply(lambda row: wdl(row, time), axis=1)
            df['gf'] = df.apply(lambda row: gf(row, time),axis=1)
            df['gs'] = df.apply(lambda row: gs(row, time),axis=1)
        except:
            df = pd.DataFrame(columns=['idresults', 'casa', 'placar', 'fora', 'data', 'liga'])
        results[time] = df
    try:
        stats = allinsights(results, liga_base, time_ou_liga='liga')
    except:
        stats = []

    sb = {
        'PremierLeague': Time.objects.filter(divisao='Premier League').order_by('time'),
        'Championship': Time.objects.filter(divisao='Championship').order_by('time'),
        'LeagueOne': Time.objects.filter(divisao='League One').order_by('time'),
        'LeagueTwo': Time.objects.filter(divisao='League Two').order_by('time'),
        'NationalLeague': Time.objects.filter(divisao='National League').order_by('time'),
    }

    tabela_liga = forma_tabela(liga_base)
    tabela_home = forma_tabela(liga_base, 'mandante')
    tabela_away = forma_tabela(liga_base, 'visitante')

    if len(stats) > 0:
        stats.insert(0, f"<b>Melhor mandante: {tabela_home['Time'][0]}</b>")
        stats.insert(1, f"<b>Melhor visitante: {tabela_away['Time'][0]}</b>")
        stats.insert(2, f"<b>Pior mandante: {tabela_home['Time'].iloc[-1]}</b>")
        stats.insert(3, f"<b>Pior visitante: {tabela_away['Time'].iloc[-1]}</b>")

    # Pegar os melhores ataques
    qtd_gols = tabela_liga.sort_values(by='GM', ascending=False)['GM'].iloc[0]
    melhores_ataques = tabela_liga[tabela_liga['GM'] == qtd_gols]
    melhores_ataques = ', '.join(melhores_ataques['Time'].values)
    if len(stats) > 0:
        stats.insert(4, f"<b>Melhor ataque: {melhores_ataques} com {qtd_gols} gols marcados</b>")

    # Pegar as melhores defesas
    qtd_gols = tabela_liga.sort_values(by='GS', ascending=True)['GS'].iloc[0]
    melhores_defesas = tabela_liga[tabela_liga['GS'] == qtd_gols]
    melhores_defesas = ', '.join(melhores_defesas['Time'].values)
    if len(stats) > 0:
        stats.insert(5, f"<b>Melhor defesa: {melhores_defesas} com {qtd_gols} gols sofridos</b>")

    # Pegar os piores ataques
    qtd_gols = tabela_liga.sort_values(by='GM', ascending=True)['GM'].iloc[0]
    piores_ataques = tabela_liga[tabela_liga['GM'] == qtd_gols]
    piores_ataques = ', '.join(piores_ataques['Time'].values)
    if len(stats) > 0:
        stats.insert(6, f"<b>Pior ataque: {piores_ataques} com {qtd_gols} gols marcados</b>")

    # Pegar as piores defesas
    qtd_gols = tabela_liga.sort_values(by='GS', ascending=False)['GS'].iloc[0]
    piores_ataques = tabela_liga[tabela_liga['GS'] == qtd_gols]
    piores_ataques = ', '.join(piores_ataques['Time'].values)
    if len(stats) > 0:
        stats.insert(7, f"<b>Pior defesa: {piores_ataques} com {qtd_gols} gols sofridos</b>")

    return render(request, 'liga.html', {'league': liga_base, 'stats': stats, 'sb':sb, 'times_da_liga':times_da_liga, 'tabela_liga':tabela_liga,
                                         'tabela_home':tabela_home, 'tabela_away':tabela_away})


def times(request, team_name):
    team_base = team_name.replace('-',' ').title()
    team_base = team_base.replace('Afc','AFC')
    resultados = get_results(team_base)

    df = pd.DataFrame.from_records(resultados.values())


    df.columns = ['idresults', 'casa', 'placar', 'fora', 'data', 'liga']
    
    df['result'] = df.apply(lambda row: wdl(row, team_base), axis=1)
    df['gf'] = df.apply(lambda row: gf(row, team_base),axis=1)
    df['gs'] = df.apply(lambda row: gs(row, team_base),axis=1)

    liga = df['liga'].unique()[0]
    tabela_time = forma_tabela(liga)
    melhores_mandantes = forma_tabela(liga, 'mandante')['Time'][:3].to_list()
    piores_mandantes = forma_tabela(liga, 'mandante')['Time'][-3:][::-1].to_list() # Começando do pior
    melhores_visitantes = forma_tabela(liga, 'visitante')['Time'][:3].to_list()
    piores_visitantes = forma_tabela(liga, 'visitante')['Time'][-3:][::-1].to_list() # Começando do pior

    
    stats = allinsights(df, team_base, time_ou_liga='time')

    for i in range(len(melhores_mandantes)):
        if team_base == melhores_mandantes[i]:
            if i == 0:
                stats.append(f"<b>{team_base} é o melhor mandante!</b>")
            else:
                stats.append(f"{team_base} é o {i+1}º melhor mandante!")

    for i in range(len(piores_mandantes)):
        if team_base == piores_mandantes[i]:
            if i == 0:
                stats.append(f"<b>{team_base} é o pior mandante!</b>")
            else:
                stats.append(f"{team_base} é o {i+1}º pior mandante!")

    for i in range(len(melhores_visitantes)):
        if team_base == melhores_visitantes[i]:
            if i == 0:
                stats.append(f"<b>{team_base} é o melhor visitante!</b>")
            else:
                stats.append(f"{team_base} é o {i+1}º melhor visitante!")

    for i in range(len(piores_visitantes)):
        if team_base == piores_visitantes[i]:
            if i == 0:
                stats.append(f"<b>{team_base} é o pior visitante!</b>")
            else:
                stats.append(f"{team_base} é o {i+1}º pior visitante!")

    times_a_aparecer = Time.objects.filter(divisao=liga).order_by('time')

    return render(request, 'time.html', {'team_name': team_base, 'resultados': resultados[::-1], 'stats': stats, 
                                         'times_a_aparecer': times_a_aparecer, 'league':liga, 'tabela_time':tabela_time})