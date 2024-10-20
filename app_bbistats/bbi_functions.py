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
    
def allinsights(df, nome, time_ou_liga=''):
    df_stats = pd.DataFrame()

    df_aux = df.copy()
    if time_ou_liga == 'time':
        n_jogos = df_aux.shape[0]
        df_stats = pd.concat([df_stats, pd.DataFrame([{'time':nome,'num_jogos':n_jogos}])])
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            n_jogos = _.shape[0]
            df_stats = pd.concat([df_stats, pd.DataFrame([{'time':time,'num_jogos':n_jogos}])])
    
    # Há quanto tempo não vence?
    df_last_win = pd.DataFrame()
    if time_ou_liga == 'time':
        ult_vitoria = df_aux[df_aux['result'] == 'win'].last_valid_index()
        if ult_vitoria is not None:
            n_jogos = df_aux.shape[0] - (ult_vitoria + 1)
        else:
            n_jogos = df_aux.shape[0]
        df_last_win = pd.concat([df_last_win, pd.DataFrame([{'time':nome,'nao_vence_faz':n_jogos}])])  
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            ult_vitoria = _[_['result'] == 'win'].last_valid_index()
            if ult_vitoria is not None:
                n_jogos = _.shape[0] - (ult_vitoria + 1)
            else:
                n_jogos = _.shape[0]
            df_last_win = pd.concat([df_last_win, pd.DataFrame([{'time':time,'nao_vence_faz':n_jogos}])])
    df_stats = pd.merge(df_stats,df_last_win,on='time',how='left')

    # Está com quantas vitórias seguidas?
    df_win_streak = pd.DataFrame()
    if time_ou_liga == 'time':
        _ = df_aux.copy()
        win_streak = 0
        for index, row in _[::-1].iterrows():
            if row['result'] == 'win':
                win_streak += 1
            else:
                break
        df_win_streak = pd.concat([df_win_streak, pd.DataFrame([{'time':nome,'win_streak':win_streak}])])
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            win_streak = 0
            end_streak = False
            for index, row in _[::-1].iterrows():
                if row['result'] == 'win':
                    if not end_streak:
                        win_streak += 1
                else:
                    break
            df_win_streak = pd.concat([df_win_streak, pd.DataFrame([{'time':time,'win_streak':win_streak}])])
    df_stats = pd.merge(df_stats,df_win_streak,on='time',how='left')

    # Está com quantas vitórias seguidas?
    df_lose_streak = pd.DataFrame()
    if time_ou_liga == 'time':
        _ = df_aux.copy()
        lose_streak = 0
        end_streak = False
        for index, row in _[::-1].iterrows():
            if row['result'] == 'loss':
                if not end_streak:
                    lose_streak += 1
            else:
                end_streak = True
        df_lose_streak = pd.concat([df_lose_streak, pd.DataFrame([{'time':nome,'lose_streak':lose_streak}])])
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            lose_streak = 0
            end_streak = False
            for index, row in _[::-1].iterrows():
                if row['result'] == 'loss':
                    if not end_streak:
                        lose_streak += 1
                else:
                    break
            df_lose_streak = pd.concat([df_lose_streak, pd.DataFrame([{'time':time,'lose_streak':lose_streak}])])
    df_stats = pd.merge(df_stats,df_lose_streak,on='time',how='left')
        
    # Quantas vitórias em 10 jogos? (Se > 7, sinalizar, se < 3, sinalizar)
    df_vitorias = pd.DataFrame()
    if time_ou_liga == 'time':
        n = 7
        wins = 1
        while wins == 1 and n <= df_aux.shape[0]:
            _ = df_aux.tail(n)
            try:
                wins = _['result'].value_counts()['win']
            except:
                wins = 0
            if wins == 1:
                n += 1
                
        if n < df_aux.shape[0]:
            n -= 1
        df_vitorias = pd.concat([df_vitorias, pd.DataFrame([{'time':nome,'vitorias':wins, '1V_qtos_jogos':n}])])
    else:
        for time in df:
            n = 7
            wins = 1
            _ = df[time]
            while wins == 1 and n <= df[time].shape[0]:
                _ = df[time].tail(n)
                try:
                    wins = _['result'].value_counts()['win']
                except:
                    wins = 0
                
                if wins == 1:
                    n += 1
            if n < df[time].shape[0]:
                n -= 1
            df_vitorias = pd.concat([df_vitorias, pd.DataFrame([{'time':nome,'vitorias':wins, '1V_qtos_jogos':n}])])
    df_stats = pd.merge(df_stats,df_vitorias,on='time',how='left')
    # Quantas derrotas em 10 jogos? (Se > 7, sinalizar, se < 3, sinalizar)
    df_derrotas = pd.DataFrame()
    if time_ou_liga == 'time':
        n = 7
        loss = 1
        while loss == 1 and n <= df_aux.shape[0]:
            _ = df_aux.tail(n)
            try:
                loss = _['result'].value_counts()['loss']
            except:
                loss = 0
            if loss == 1:
                n += 1
        if n < df_aux.shape[0]:
            n -= 1
        df_derrotas = pd.concat([df_derrotas, pd.DataFrame([{'time':nome,'derrotas':loss, '1D_qtos_jogos':n}])])
    elif time_ou_liga == 'liga':
        for time in df:
            n = 7
            loss = 1
            _ = df[time]
            while loss == 1 and n <= df[time].shape[0]:
                _ = df[time].tail(n)
                try:
                    loss = _['result'].value_counts()['win']
                except:
                    loss = 0
                if loss == 1:
                    n += 1
        if n < df[time].shape[0]:
            n -= 1
            df_derrotas = pd.concat([df_derrotas, pd.DataFrame([{'time':nome,'vitorias':wins, '1D_qtos_jogos':n}])])
    df_stats = pd.merge(df_stats,df_derrotas,on='time',how='left')

    # Há quanto tempo não perde?
    df_last_loss = pd.DataFrame()
    if time_ou_liga == 'time':
        ult_derrota = df_aux[df_aux['result'] == 'loss'].last_valid_index()
        if ult_derrota is not None:
            n_jogos = df_aux.shape[0] - (ult_derrota + 1)
        else:
            n_jogos = df_aux.shape[0]
        df_last_loss = pd.concat([df_last_loss, pd.DataFrame([{'time':nome,'nao_perde_faz':n_jogos}])]) 
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            ult_derrota = _[_['result'] == 'loss'].last_valid_index()
            if ult_derrota is not None:
                n_jogos = _.shape[0] - (ult_derrota + 1)
            else:
                n_jogos = _.shape[0]
            df_last_loss = pd.concat([df_last_loss, pd.DataFrame([{'time':time,'nao_perde_faz':n_jogos}])])
    df_stats = pd.merge(df_stats,df_last_loss,on='time',how='left')

    # Quantos pontos conquistados nos últimos 5 jogos?
    df_pts_5 = pd.DataFrame(columns=['time'])
    form_5 = ''
    if time_ou_liga == 'time':
        _ = df_aux.tail(5)
        for index, row in _.iterrows():
            form_5 += row['result'][0].upper()
        try:
            win = _['result'].value_counts()['win']
        except:
            win = 0
        try:
            draw = _['result'].value_counts()['draw']
        except:
            draw = 0
        pts = win*3+draw
        df_pts_5 = pd.concat([df_pts_5, pd.DataFrame([{'time':nome,'pts_5':pts}])])
    df_stats = pd.merge(df_stats,df_pts_5,on='time',how='left')

    

    df_home_away_games = pd.DataFrame(columns=['time'])
    if time_ou_liga == 'time':

        # Quantos gols feitos nos últimos jogos?
        df_gf = pd.DataFrame(columns=['time'])
        if time_ou_liga == 'time':
            gf = df_aux['gf'].tail(5).sum()
            media = df_aux['gf'].tail(5).mean()
            df_gf = pd.concat([df_gf, pd.DataFrame([{'time':nome,'gf_ult5':gf,'gf_ult5_media':media}])])

            df_stats = pd.merge(df_stats,df_gf,on='time',how='left')
        # Quantos gols sofridos nos últimos jogos?
        df_gs = pd.DataFrame(columns=['time'])
        if time_ou_liga == 'time':
            gs = df_aux['gs'].tail(5).sum()
            media = df_aux['gs'].tail(5).mean()
            df_gs = pd.concat([df_gs, pd.DataFrame([{'time':nome,'gs_ult5':gs,'gs_ult5_media':media}])])
            
        df_stats = pd.merge(df_stats,df_gs,on='time',how='left')

        _ = df_aux.copy()
        _ = _[_['casa'] == nome].reset_index(drop=True)
        num_jogos_casa = _.shape[0]
        
        ult_vitoria_casa = _[_['result'] == 'win'].last_valid_index()
        if ult_vitoria_casa is not None:
            ult_vitoria_casa = _.shape[0] - (ult_vitoria_casa + 1)
        else:
            ult_vitoria_casa = _.shape[0]
            
        ult_derrota_casa = _[_['result'] == 'loss'].last_valid_index()
        if ult_derrota_casa is not None:
            ult_derrota_casa = _.shape[0] - (ult_derrota_casa + 1)
        else:
            ult_derrota_casa = _.shape[0]
        
        _ = df_aux.copy()
        _ = _[_['fora'] == nome].reset_index(drop=True)
        
        num_jogos_fora = _.shape[0]
        ult_vitoria_fora = _[_['result'] == 'win'].last_valid_index()
        if ult_vitoria_fora is not None:
            ult_vitoria_fora = _.shape[0] - (ult_vitoria_fora + 1)
        else:
            ult_vitoria_fora = _.shape[0]
            
        ult_derrota_fora = _[_['result'] == 'loss'].last_valid_index()
        if ult_derrota_fora is not None:
            ult_derrota_fora = _.shape[0] - (ult_derrota_fora + 1)
        else:
            ult_derrota_fora = _.shape[0]
        df_home_away_games = pd.concat([df_home_away_games, pd.DataFrame([{'time':nome,
                                                                        'num_jogos_casa':num_jogos_casa,
                                                                        'casa_nao_vence_faz':ult_vitoria_casa,
                                                                        'casa_nao_perde_faz':ult_derrota_casa,
                                                                        'num_jogos_fora':num_jogos_fora,
                                                                        'fora_nao_vence_faz':ult_vitoria_fora,
                                                                        'fora_nao_perde_faz':ult_derrota_fora}])])
    elif time_ou_liga == 'liga':
        for time in df:
            _ = df[time]
            _ = _[_['casa'] == time].reset_index(drop=True)
            num_jogos_casa = _.shape[0]
            
            ult_vitoria_casa = _[_['result'] == 'win'].last_valid_index()
            if ult_vitoria_casa is not None:
                ult_vitoria_casa = _.shape[0] - (ult_vitoria_casa + 1)
            else:
                ult_vitoria_casa = _.shape[0]
            ult_vitoria_casa = int(ult_vitoria_casa)
                
            ult_derrota_casa = _[_['result'] == 'loss'].last_valid_index()
            if ult_derrota_casa is not None:
                ult_derrota_casa = _.shape[0] - (ult_derrota_casa + 1)
            else:
                ult_derrota_casa = _.shape[0]
            
            _ = df[time]
            _ = _[_['fora'] == time].reset_index(drop=True)
            
            num_jogos_fora = _.shape[0]
            ult_vitoria_fora = _[_['result'] == 'win'].last_valid_index()
            if ult_vitoria_fora is not None:
                ult_vitoria_fora = _.shape[0] - (ult_vitoria_fora + 1)
            else:
                ult_vitoria_fora = _.shape[0]
                
            ult_derrota_fora = _[_['result'] == 'loss'].last_valid_index()
            if ult_derrota_fora is not None:
                ult_derrota_fora = _.shape[0] - (ult_derrota_fora + 1)
            else:
                ult_derrota_fora = _.shape[0]
            df_home_away_games = pd.concat([df_home_away_games, pd.DataFrame([{'time':time,
                                                                            'num_jogos_casa':num_jogos_casa,
                                                                            'casa_nao_vence_faz':ult_vitoria_casa,
                                                                            'casa_nao_perde_faz':ult_derrota_casa,
                                                                            'num_jogos_fora':num_jogos_fora,
                                                                            'fora_nao_vence_faz':ult_vitoria_fora,
                                                                            'fora_nao_perde_faz':ult_derrota_fora}])])
    df_stats = pd.merge(df_stats,df_home_away_games,on='time',how='left')

    _ = df_stats.copy()
    insights = []
    for row in _.iterrows():
        stats = row[1]
        # Se está invicto, mostre.
        # Se não está invicto, mostre há quanto tempo não perde, e se está invicto em casa ou fora.
        if stats['num_jogos'] == stats['nao_perde_faz']:
            insights.append(f"{stats['time']} está invicto!")
        else:
            if stats['nao_perde_faz'] >= 5:
                insights.append(f"{stats['time']} está invicto há {int(stats['nao_perde_faz'])} jogos!")
            if stats['num_jogos_casa'] == stats['casa_nao_perde_faz']:
                insights.append(f"{stats['time']} está invicto em casa!")
            elif stats['casa_nao_perde_faz'] >= 5:
                insights.append(f"{stats['time']} está invicto em casa há {int(stats['casa_nao_perde_faz'])} jogos!")
            if stats['num_jogos_fora'] == stats['fora_nao_perde_faz']:
                insights.append(f"{stats['time']} está invicto fora!")
            elif stats['fora_nao_perde_faz'] >= 5:
                insights.append(f"{stats['time']} está invicto fora há {int(stats['fora_nao_perde_faz'])} jogos!")

            
    
    for row in _.iterrows():
        stats = row[1]
        if stats['win_streak'] >= 3:
            insights.append(f"{stats['time']} está na {int(stats['win_streak'])}ª vitória seguida!")
        elif stats['lose_streak'] >= 3:
            insights.append(f"{stats['time']} está na {int(stats['lose_streak'])}ª derrota seguida!")

    for row in _.iterrows():
        stats = row[1]
        if stats['num_jogos'] == stats['nao_vence_faz']:
            insights.append(f"{stats['time']} ainda não venceu em todos os seus {stats['num_jogos']} jogos!")
        else:
            if stats['nao_vence_faz'] >= 5:
                insights.append(f"{stats['time']} não vence há {stats['nao_vence_faz']} jogos!")
            if stats['num_jogos_casa'] == stats['casa_nao_vence_faz']:
                insights.append(f"{stats['time']} ainda não venceu em casa!")
            elif stats['casa_nao_vence_faz'] >= 5:
                insights.append(f"{stats['time']} não vence em casa há {int(stats['casa_nao_vence_faz'])} jogos!")
            if stats['num_jogos_fora'] == stats['fora_nao_vence_faz']:
                insights.append(f"{stats['time']} ainda não venceu fora!")
            elif stats['fora_nao_vence_faz'] >= 5:
                insights.append(f"{stats['time']} não vence fora há {int(stats['fora_nao_vence_faz'])} jogos!")

            
    
    if time_ou_liga == 'time':
        insights.append(f"Forma: {form_5}")
        for row in _.iterrows():

            stats = row[1]
            if stats['1V_qtos_jogos'] > 7:
                insights.append(f"{stats['time']} possui 1 vitória em {int(stats['1V_qtos_jogos'])} jogos.")
            elif stats['derrotas'] > 7:
                if stats['num_jogos'] >= 10:
                    insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrotas em 10 jogos.")
                else:
                    insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrotas em {stats['num_jogos']} jogos.")

                if stats['vitorias'] < 3 and stats['vitorias'] > 0:
                    if stats['num_jogos'] >= 10:
                        insights.append(f"{stats['time']} possui {int(stats['vitorias'])} vitórias em 10 jogos.")
                    else:
                        insights.append(f"{stats['time']} possui {int(stats['vitorias'])} vitórias em {stats['num_jogos']} jogos.")

            if stats['1D_qtos_jogos'] > 7:
                insights.append(f"{stats['time']} possui 1 derrota em {int(stats['1D_qtos_jogos'])} jogos.")
            elif stats['vitorias'] > 7:
                if stats['num_jogos'] >= 10:
                    insights.append(f"{stats['time']} possui {int(stats['vitorias'])} vitórias em 10 jogos.")
                    if stats['derrotas'] < 3 and stats['derrotas'] > 0:
                        if stats['derrotas'] == 1:
                            insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrota em 10 jogos.")
                        else:
                            insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrotas em 10 jogos.")
                else:
                    insights.append(f"{stats['time']} possui {int(stats['vitorias'])} vitórias em {stats['num_jogos']} jogos.")
                    if stats['derrotas'] < 3 and stats['derrotas'] > 0:
                        if stats['derrotas'] == 1:
                            insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrota em {stats['num_jogos']} jogos.")
                        else:
                            insights.append(f"{stats['time']} possui {int(stats['derrotas'])} derrotas em {stats['num_jogos']} jogos.")
            
            
            if stats['num_jogos'] >= 5:
                if stats['pts_5'] >= 2:
                    insights.append(f"{stats['time']} fez {int(stats['pts_5'])} pontos nos últimos 5 jogos!")
                elif stats['pts_5'] == 1:
                    insights.append(f"{stats['time']} fez {int(stats['pts_5'])} ponto nos últimos 5 jogos!")
        
        for row in _.iterrows():
            stats = row[1]       
            if stats['gf_ult5'] == 0:
                insights.append(f"{stats['time']} não fez gols nos últimos 5 jogos!")
            elif stats['gf_ult5_media'] < 1:
                if stats['num_jogos'] >= 5:
                    insights.append(f"{stats['time']} fez uma média de {round(stats['gf_ult5_media'],2)} gols nos últimos 5 jogos")
                else:
                    insights.append(f"{stats['time']} fez uma média de {round(stats['gf_ult5_media'],2)} gols nos últimos {stats['num_jogos']} jogos")
        
        for row in _.iterrows():
            stats = row[1]
            if stats['gs_ult5'] == 0:
                insights.append(f"{stats['time']} não sofreu gols nos últimos 5 jogos!")
            elif stats['gs_ult5_media'] >= 1.5:
                if stats['num_jogos'] >= 5:
                    insights.append(f"{stats['time']} sofreu uma média de {round(stats['gs_ult5_media'],2)} gols nos últimos 5 jogos")
                else:
                    insights.append(f"{stats['time']} sofreu uma média de {round(stats['gs_ult5_media'],2)} gols nos últimos {stats['num_jogos']} jogos")
    # print(insights)
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