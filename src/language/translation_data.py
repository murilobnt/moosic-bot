import json

data = {
    'pt_br': {
        "er_con" : "Você precisa estar conectado a um canal de voz",
        "er_conb" : "Não há conexão com o bot",
        "er_down" : "Houve um erro com o download de um item",
        "er_index" : "Especifique um índice válido de música",
        "er_ytdl" : "Algo deu errado",
        "er_url" : "Algo deu errado com a extração de informações",
        "er_conc" : "Há um problema de conexão com canal. Tchau tchau",
        "er_perm" : "Não tenho permissão para me conectar ou para falar no canal",
        "song_add" : "Adicionado [{title}]({url}), por {mention}",
        "pl_add" : "Adicionado {pl_len} itens, por {mention}",
        "er_nosong" : "Não há música tocando",
        "er_skipindex" : "Especifique um número válido de músicas para pular",
        "er_skiparg" : "Argumento inválido",
        "skip_succ" : "Pulei {how_many} música(s)",
        "er_paused" : "A música já está pausada",
        "er_nopause" : "Não há música pausada",
        "er_seekarg" : "Forneça uma timestamp no formato HORAS:MINUTOS:SEGUNDOS que faça sentido",
        "er_npdat" : "Houve um problema em pegar os dados do tempo da música",
        "np_succnorm" : "Tocando [{title}]({weburl}), por {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Tocando [{title}]({weburl}), por {mention}\nLIVE por {formatted_elapsed} no servidor",
        "q_norep" : "Sem repetição",
        "q_qrep" : "Repetição: Fila",
        "q_songrep" : "Repetição: {song}",
        "q_np" : " restantes (tocando agora)",
        "q_nplive" : " (tocando agora)",
        "q_page"   : """
```arm
Fila de reprodução: Página {page_plus} de {last_page_plus}

{songs}

{in_loop}
```
        """,
        "dc_msg" : "Saindo. Tchau tchau",
        "er_vsv" : "Você precisa estar no mesmo canal de voz que o bot",
        "er_vr" : "Não há conexão do bot com o servidor",
        "er_vns" : "Não há músicas na fila",
        "er_rmindex" : "Especifique um índice válido de música na fila",
        "loop_lq" : "de repetição de fila",
        "loop_ls" : "de repetição do item",
        "loop_noloop" : "sem repetição",
        "loop_succ" : "Modo {mode} ativado",
        "er_playdl" : """
```
Whoops! Houve um erro de download para {title}. Ele será pulado :)
```
        """,
        "play_np" : "Tocando agora",
        "inactive_notice" : "Por estar inativo, vou sair da call. Tchau tchau!",
        "alone_notice" : "Estou a sós na call por um tempo. Saindo!",
        "q_next" : "Próxima música"
    },
    'us_en': {
        "er_con" : "You need to be connected to a voice channel",
        "er_conb" : "There is no connection with the bot",
        "er_down" : "There was an error with the download of the item",
        "er_index" : "Specify a valid song index",
        "er_ytdl" : "Something went wrong",
        "er_url" : "Something went wrong about the extraction of the information",
        "er_conc" : "There is a conection problem with the channel. Bye bye",
        "er_perm" : "I don't have permission to connect or speak in the channel",
        "song_add" : "Added [{title}]({url}), by {mention}",
        "pl_add" : "Added {pl_len} items, by {mention}",
        "er_nosong" : "There is no song playing",
        "er_skipindex" : "Specify a valid number of songs to skip",
        "er_skiparg" : "Invalid argument",
        "skip_succ" : "Skipped {how_many} song(s)",
        "er_paused" : "The song is already paused",
        "er_nopause" : "There is no song paused",
        "er_seekarg" : "Specify a timestamp in the HOURS:MINUTES:SECONDS format that make sense",
        "er_npdat" : "There was a problem in fetching the time data of the song",
        "np_succnorm" : "Playing [{title}]({weburl}), by {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Playing [{title}]({weburl}), by {mention}\nLIVE for {formatted_elapsed} in the server",
        "q_norep" : "No loop",
        "q_qrep" : "Looping: Queue",
        "q_songrep" : "Looping: {song}",
        "q_np" : " remaining (now playing)",
        "q_nplive" : " (now playing)",
        "q_page"   : """
```arm
Song queue: Page {page_plus} of {last_page_plus}

{songs}

{in_loop}
```
        """,
        "dc_msg" : "Leaving. Bye bye",
        "er_vsv" : "You need to be in the same voice channel of the bot",
        "er_vr" : "There is no connection from the bot with the server",
        "er_vns" : "There is no songs in the queue",
        "er_rmindex" : "Specify a valid song index of the queue",
        "loop_lq" : "Queue loop",
        "loop_ls" : "Song loop",
        "loop_noloop" : "No loop",
        "loop_succ" : "{mode} mode activated",
        "er_playdl" : """
```
Whoops! There was an download error for {title}. It will be skipped :)
```
        """,
        "play_np" : "Now playing",
        "inactive_notice" : "For I'm inactive, I'm leaving the vc. Bye bye!",
        "alone_notice" : "I'm alone in the vc for a while. Leaving!",
        "q_next" : "Next song"
    },
    'es': {
        "er_con" : "Debe estar conectado a un canal de voz",
        "er_conb" : "No hay conexión con el bot",
        "er_down" : "Hubo un error al descargar un elemento",
        "er_index" : "Especifica un índice de música válido",
        "er_ytdl" : "Algo salió mal",
        "er_url" : "Algo salió mal al extraer información",
        "er_conc" : "Hay un problema de conexión con el canal. Adiooos",
        "er_perm" : "No tengo permiso para iniciar sesión o hablar en el canal",
        "song_add" : "Agregó [{title}]({url}), por {mention}",
        "pl_add" : "Agregó {pl_len} elementos, por {mention}",
        "er_nosong" : "No hay música sonando",
        "er_skipindex" : "Especifique un número válido de musicas para saltar",
        "er_skiparg" : "Argumento no válido",
        "skip_succ" : "Salteado {how_many} música(s)",
        "er_paused" : "La música ya esta pausada",
        "er_nopause" : "No hay música pausada",
        "er_seekarg" : "Proporcione una marca de tiempo en el formato HORAS: SEGUNDOS: MINUTOS que tenga sentido",
        "er_npdat" : "Hubo un problema al obtener los datos de tempo de la música",
        "np_succnorm" : "Tocando [{title}]({weburl}), por {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Tocando [{title}]({weburl}), por {mention}\nLIVE durante {formatted_elapsed} en el servidor",
        "q_norep" : "Sin repetición",
        "q_qrep" : "Repetición: Cola",
        "q_songrep" : "Repetición: {song}",
        "q_np" : " restante (tocando ahora)",
        "q_nplive" : " (tocando ahora)",
        "q_page"   : """
```arm
Cola de reproducción: Página {page_plus} de {last_page_plus}

{songs}

{in_loop}
```
        """,
        "dc_msg" : "Estoy saliendo. Adioooos",
        "er_vsv" : "Debes estar en el mismo canal de voz que el bot",
        "er_vr" : "No hay conección del bot con el servidor",
        "er_vns" : "No hay músicas en la cola",
        "er_rmindex" : "Proprociona un índice de música válido en la cola",
        "loop_lq" : "de reintento en cola",
        "loop_ls" : "de reintento en música",
        "loop_noloop" : "sin repetición",
        "loop_succ" : "Modo {mode} habilitado",
        "er_playdl" : """
```
Whoops! Hubo un error de download para {title}. Será saltado :)
```
        """,
        "play_np" : "Tocando ahora",
        "inactive_notice" : "Porque estoy inactivo, me voy a salir del voice. ¡Adioooos!",
        "alone_notice" : "Estoy solo en el voice por un tiempo. ¡Dejando!",
        "q_next" : "Siguiente música"
    }
}
