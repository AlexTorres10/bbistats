import pandas as pd
import numpy as np

def wdl(df, time):
    gh = int(df['placar'].split('-')[0])
    ga = int(df['placar'].split('-')[1])
    if gh == ga:
        return 'draw'
    else:
        homeaway = 'home' if df['casa'] == time else 'away'
        if homeaway == 'home':
            if gh > ga:
                return 'win'
            else:
                return 'loss'
        else:
            if ga > gh:
                return 'win'
            else:
                return 'loss'
            
def gf(df, time):
    gh = int(df['placar'].split('-')[0])
    ga = int(df['placar'].split('-')[1])
    homeaway = 'home' if df['casa'] == time else 'away'
    if homeaway == 'home':
        return gh
    else:
        return ga
    
def gs(df, time):
    gh = int(df['placar'].split('-')[0])
    ga = int(df['placar'].split('-')[1])
    homeaway = 'home' if df['casa'] == time else 'away'
    if homeaway == 'home':
        return ga
    else:
        return gh
    
def detectar_fase_estendida(df, nome_time, limite_max_vitorias=2, limite_min_vitorias=5, limite_max_derrotas=2, limite_min_derrotas=5):
    """
    Verifica a maior sequência possível em que:
    - as vitórias são <= limite_max_vitorias (má fase)
    - as vitórias são >= limite_min_vitorias (boa fase)
    - as derrotas são >= limite_min_derrotas (má fase)
    - as derrotas são <= limite_max_derrotas (boa fase)
    """
    insights = []
    total_jogos = df.shape[0]

    def contar_jogos(cond_func):
        for n in range(7, total_jogos + 1):
            subset = df.tail(n)
            resultados = subset['result'].value_counts()
            v = resultados.get('win', 0)
            d = resultados.get('loss', 0)
            if not cond_func(v, d):
                return n - 1, subset.tail(n - 1)['result'].value_counts()
        return total_jogos, df.tail(total_jogos)['result'].value_counts()

    # Má fase por vitórias
    n_vit_ruim, res_vit_ruim = contar_jogos(lambda v, d: v <= limite_max_vitorias)
    if n_vit_ruim >= 7 and res_vit_ruim.get('win', 0) <= limite_max_vitorias:
        vitorias = res_vit_ruim.get('win', 0)
        if vitorias == 0:
            insights.append(f"{nome_time} não venceu nenhum dos últimos {n_vit_ruim} jogos.")
        else:
            insights.append(f"{nome_time} venceu apenas {vitorias} dos últimos {n_vit_ruim} jogos.")

    # Boa fase por vitórias
    n_vit_bom, res_vit_bom = contar_jogos(lambda v, d: v >= limite_min_vitorias)
    if n_vit_bom >= 7 and res_vit_bom.get('win', 0) >= limite_min_vitorias:
        insights.append(f"{nome_time} venceu {res_vit_bom.get('win', 0)} dos últimos {n_vit_bom} jogos. Boa fase!")

    # Má fase por derrotas
    n_derrotas_ruim, res_derrotas_ruim = contar_jogos(lambda v, d: d >= limite_min_derrotas)
    if n_derrotas_ruim >= 7 and res_derrotas_ruim.get('loss', 0) >= limite_min_derrotas:
        insights.append(f"{nome_time} perdeu {res_derrotas_ruim.get('loss', 0)} dos últimos {n_derrotas_ruim} jogos.")

    # Boa fase por poucas derrotas
    n_derrotas_bom, res_derrotas_bom = contar_jogos(lambda v, d: d <= limite_max_derrotas)
    if n_derrotas_bom >= 7 and res_derrotas_bom.get('loss', 0) <= limite_max_derrotas:
        derrotas = res_derrotas_bom.get('loss', 0)
        if derrotas == 0:
            insights.append(f"{nome_time} está invicto há {n_derrotas_bom} jogos.")
        else:
            insights.append(f"{nome_time} sofreu apenas {derrotas} derrotas nos últimos {n_derrotas_bom} jogos.")

    return {
        'time': nome_time,
        'jogos_analisados': total_jogos
    }, insights

def streaks(df, nome_time):
    win_streak = 0
    lose_streak = 0
    for res in reversed(df['result'].tolist()):
        if res == 'win':
            if lose_streak == 0:
                win_streak += 1
            else:
                break
        elif res == 'loss':
            if win_streak == 0:
                lose_streak += 1
            else:
                break
        else:
            break

    return {
        'time': nome_time,
        'win_streak': win_streak,
        'lose_streak': lose_streak
    }, win_streak, lose_streak

def pontos_ultimos_jogos(df, nome_time, n=5):
    ultimos_n = df.tail(n)
    resultados = ultimos_n['result'].value_counts()
    win = resultados.get('win', 0)
    draw = resultados.get('draw', 0)
    pontos = win * 3 + draw
    return {'time': nome_time, 'pts_ult5': pontos}, pontos

def allinsights(df, nome, time_ou_liga=''):
    df_stats = pd.DataFrame()
    insights = []

    if time_ou_liga == 'time':
        estat_forma, insights_forma = detectar_fase_estendida(df, nome)
        estat_streak, win_streak, lose_streak = streaks(df, nome)
        estat_pontos, pontos = pontos_ultimos_jogos(df, nome)

        if win_streak >= 3:
            insights.append(f"{nome} está na {win_streak}ª vitória seguida!")
        if lose_streak >= 3:
            insights.append(f"{nome} está na {lose_streak}ª derrota seguida!")

        if pontos >= 10:
            insights.append(f"{nome} somou {pontos} pontos nos últimos 5 jogos. Excelente fase!")
        elif pontos <= 2:
            if pontos == 0:
                insights.append(f"{nome} não pontuou nos últimos 5 jogos.")
            elif pontos == 1:
                insights.append(f"{nome} somou apenas {pontos} ponto nos últimos 5 jogos.")
            else:
                insights.append(f"{nome} somou apenas {pontos} pontos nos últimos 5 jogos.")

        insights.extend(insights_forma)

    elif time_ou_liga == 'liga':
        estat_list = []
        for time in df:
            estat_forma, insights_forma = detectar_fase_estendida(df[time], time)
            estat_streak, win_streak, lose_streak = streaks(df[time], time)
            estat_pontos, pontos = pontos_ultimos_jogos(df[time], time)

            estat_list.append({
                **estat_forma,
                **estat_streak,
                **estat_pontos
            })

            if win_streak >= 3:
                insights.append(f"{time} está na {win_streak}ª vitória seguida!")
            if lose_streak >= 3:
                insights.append(f"{time} está na {lose_streak}ª derrota seguida!")

            # Só adiciona estatística de pontos se tiver pelo menos 5 jogos
            if df[time].shape[0] >= 5:
                if pontos >= 10:
                    insights.append(f"{time} somou {pontos} pontos nos últimos 5 jogos. Excelente fase!")
                elif pontos <= 2:
                    if pontos == 0:
                        insights.append(f"{time} não pontuou nos últimos 5 jogos.")
                    elif pontos == 1:
                        insights.append(f"{time} somou apenas {pontos} ponto nos últimos 5 jogos.")
                    else:
                        insights.append(f"{time} somou apenas {pontos} pontos nos últimos 5 jogos.")

            insights.extend(insights_forma)

    return insights


def atualiza_tabela(tabela, home, away, result, tipo_tabela=''):
    # Aqui estou contando que o que está no banco de dados já está nos conformes.
    homescore = int(result.split('-')[0])
    awayscore = int(result.split('-')[1])
    for team in [home, away]:
        if team == home:
            ishome = True
        else:
            ishome = False
        if tipo_tabela == '':
            if ishome:
                gd = homescore-awayscore
                tabela['GM'] = np.where(tabela['Time'] == team,tabela['GM']+homescore,tabela['GM'])
                tabela['GS'] = np.where(tabela['Time'] == team,tabela['GS']+awayscore,tabela['GS'])
            else:
                gd = awayscore-homescore
                tabela['GM'] = np.where(tabela['Time'] == team,tabela['GM']+awayscore,tabela['GM'])
                tabela['GS'] = np.where(tabela['Time'] == team,tabela['GS']+homescore,tabela['GS'])
            #Mais um jogo
            tabela['J'] = np.where(tabela['Time'] == team,tabela['J']+1,tabela['J'])
            tabela['SG'] = np.where(tabela['Time'] == team,tabela['SG']+gd,tabela['SG'])

            if gd > 0:
                tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+3,tabela['Pts'])
                tabela['V'] = np.where(tabela['Time'] == team,tabela['V']+1,tabela['V'])
            elif gd == 0:
                tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+1,tabela['Pts'])
                tabela['E'] = np.where(tabela['Time'] == team,tabela['E']+1,tabela['E'])
            else:
                tabela['D'] = np.where(tabela['Time'] == team,tabela['D']+1,tabela['D'])
        elif tipo_tabela == 'mandante':
            if ishome:
                gd = homescore-awayscore
                tabela['GM'] = np.where(tabela['Time'] == team,tabela['GM']+homescore,tabela['GM'])
                tabela['GS'] = np.where(tabela['Time'] == team,tabela['GS']+awayscore,tabela['GS'])

                tabela['J'] = np.where(tabela['Time'] == team,tabela['J']+1,tabela['J'])
                tabela['SG'] = np.where(tabela['Time'] == team,tabela['SG']+gd,tabela['SG'])

                if gd > 0:
                    tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+3,tabela['Pts'])
                    tabela['V'] = np.where(tabela['Time'] == team,tabela['V']+1,tabela['V'])
                elif gd == 0:
                    tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+1,tabela['Pts'])
                    tabela['E'] = np.where(tabela['Time'] == team,tabela['E']+1,tabela['E'])
                else:
                    tabela['D'] = np.where(tabela['Time'] == team,tabela['D']+1,tabela['D'])
        elif tipo_tabela == 'visitante':
            if not ishome:
                gd = awayscore-homescore
                tabela['GM'] = np.where(tabela['Time'] == team,tabela['GM']+homescore,tabela['GM'])
                tabela['GS'] = np.where(tabela['Time'] == team,tabela['GS']+awayscore,tabela['GS'])

                tabela['J'] = np.where(tabela['Time'] == team,tabela['J']+1,tabela['J'])
                tabela['SG'] = np.where(tabela['Time'] == team,tabela['SG']+gd,tabela['SG'])

                if gd > 0:
                    tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+3,tabela['Pts'])
                    tabela['V'] = np.where(tabela['Time'] == team,tabela['V']+1,tabela['V'])
                elif gd == 0:
                    tabela['Pts'] = np.where(tabela['Time'] == team,tabela['Pts']+1,tabela['Pts'])
                    tabela['E'] = np.where(tabela['Time'] == team,tabela['E']+1,tabela['E'])
                else:
                    tabela['D'] = np.where(tabela['Time'] == team,tabela['D']+1,tabela['D'])