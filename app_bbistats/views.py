from django.shortcuts import render
from django.db import connection
from .models import *
from .bbi_functions import *

def get_results(time):
    return Result.objects.filter(casa=time) | Result.objects.filter(fora=time).order_by('data')

def forma_tabela(divisao):
    times_da_liga = Time.objects.filter(divisao=divisao).order_by('time')
    colunas_tabela = ['Time','J','V','E','D','GM','GS','SG','Pts']
    tabela = pd.DataFrame(columns=colunas_tabela)

    team_dataframes = []
    for time in times_da_liga:
        novo_time = {'Time': time.time, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GM': 0, 'GS': 0, 'SG': 0, 'Pts': 0}
        tabela = pd.concat([tabela, pd.DataFrame([novo_time])], ignore_index=True)

    times_que_perderam_pts = ['Reading', 'Wigan Athletic']
    pontos_a_tirar = {'Reading': 4, 'Wigan Athletic': 8}

    for team in times_que_perderam_pts:
        if team in tabela['Time'].values:
            # Subtract points for the specific team
            tabela.loc[tabela['Time'] == team, 'Pts'] -= pontos_a_tirar.get(team, 0)

    resultados_da_liga = Result.objects.filter(liga=divisao).order_by('data')
    for result in resultados_da_liga:
        atualiza_tabela(tabela, result.casa, result.fora, result.placar)
    tabela = tabela.sort_values(by=['Pts','SG','GM'], ascending=False,ignore_index=False).reset_index(drop=True).reset_index()
    tabela['index'] = tabela['index']+1
    tabela = tabela.rename(columns={'index':'Pos'})
    return tabela


# Request permite acessar os dados daquela página
def home(request):
    # request = dados, e a página HTML responsável

    ligas = ['Premier League', 'Championship', 'League One', 'League Two', 'National League']
    tabela_da_liga = {}
    show_tabela = {}
    for l in ligas:
        tabela_da_liga[l] = forma_tabela(l)
        show_tabela[l] = tabela_da_liga[l].head(7)[['Time', 'J', 'SG', 'Pts']]

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
        df.columns = ['idresults', 'casa', 'placar', 'fora', 'data', 'liga']
        df['result'] = df.apply(lambda row: wdl(row, time), axis=1)
        df['gf'] = df.apply(lambda row: gf(row, time),axis=1)
        df['gs'] = df.apply(lambda row: gs(row, time),axis=1)
        results[time] = df
    
    stats = allinsights(results, liga_base, time_ou_liga='liga')

    sb = {
        'PremierLeague': Time.objects.filter(divisao='Premier League').order_by('time'),
        'Championship': Time.objects.filter(divisao='Championship').order_by('time'),
        'LeagueOne': Time.objects.filter(divisao='League One').order_by('time'),
        'LeagueTwo': Time.objects.filter(divisao='League Two').order_by('time'),
        'NationalLeague': Time.objects.filter(divisao='National League').order_by('time'),
    }

    tabela_liga = forma_tabela(liga_base)

    return render(request, 'liga.html', {'league': liga_base, 'stats': stats, 'sb':sb, 'times_da_liga':times_da_liga, 'tabela_liga':tabela_liga})


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
    
    stats = allinsights(df, team_base, time_ou_liga='time')

    times_a_aparecer = Time.objects.filter(divisao=liga).order_by('time')

    return render(request, 'time.html', {'team_name': team_base, 'resultados': resultados[::-1], 'stats': stats, 
                                         'times_a_aparecer': times_a_aparecer, 'league':liga, 'tabela_time':tabela_time})