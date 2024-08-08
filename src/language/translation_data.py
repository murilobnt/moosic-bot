data = {
    'pt_br': {
        "desc_mp" : "Tocador de áudio de vídeos do YouTube",
        "desc_ss" : "Configurações para o servidor",

        "er_con" : "Você precisa estar conectado a um canal de voz",
        "er_conb" : "Não há conexão com o bot",
        "er_down" : "Houve um erro com o download de um item",
        "er_index" : "Especifique um índice válido de música",
        "er_ytdl" : "Algo deu errado",
        "er_url" : "Algo deu errado com a extração de informações",
        "er_conc" : "Há um problema de conexão com canal. Tchau tchau",
        "er_perm" : "Não tenho permissão para me conectar ou para falar no canal",
        "er_shoutlen" : "Índice inválido de escolha. A operação foi cancelada",
        "er_shtimeout" : "30 segundos se passaram. A operação foi cancelada",
        "er_himalformed" : "Algo deu errado. Por favor, verifique se a URL é valida",
        "er_hispotifyuri" : "Ainda não suportado. Apenas /playlist e /track são suportados no momento",
        "er_hidomain" : "Domínio não suportado. Apenas YouTube e Spotify são suportados no momento",
        "song_add" : "Adicionado [{title}]({url}) na posição {index} da fila, por {mention}",
        "pl_add" : "Adicionado {pl_len} itens, por {mention}",
        "er_nosong" : "Não há música tocando",
        "er_skipindex" : "Especifique um número válido de músicas para pular",
        "er_skiparg" : "Argumento inválido",
        "skip_succ" : "Pulei {how_many} música(s)",
        "er_paused" : "A música já está pausada",
        "er_nopause" : "Não há música pausada",
        "er_seekarg" : "Forneça uma timestamp no formato HORAS:MINUTOS:SEGUNDOS que faça sentido",
        "er_npdat" : "Houve um problema em pegar os dados do tempo da música",
        "np_succnorm" : "Tocando {index}. [{title}]({weburl}), por {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Tocando {index}. [{title}]({weburl}), por {mention}\nLIVE por {formatted_elapsed} no servidor",
        "q_norep" : "Sem repetição",
        "q_qrep" : "Repetição: Fila",
        "q_songrep" : "Repetição: {song}",
        "q_np" : "(tocando agora)",
        "q_remaining" : "restantes",
        "q_page"   : """
```markdown
Fila de reprodução: <Pagina {page_plus} de {last_page_plus}>

{songs}

# {in_loop}
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
        "play_duration" : "Duração",
        "play_shcancel" : "Operação cancelada",
        "play_by" : "por",
        "play_buildt" : """
```markdown
# Por favor, faça sua escolha de música

{songs_str}

[c] : <Cancelar>
```
""",
        "inactive_notice" : "Por estar inativo, vou sair da call. Tchau tchau!",
        "alone_notice" : "Estou a sós na call por um tempo. Saindo!",
        "q_next" : "Próxima música",

        "help_it" : "Categorias",
        "help_en" : "Digite {help.clean_prefix}{help.invoked_with} <comando> para mais informações sobre algum comando.\nAlternativamente, {help.clean_prefix}{help.invoked_with} categoria para mais informações sobre uma categoria.",

        "disconnect" : "Desconecta o bot da chamada e encerra tudo",
        "loop" : "Altera o modo de loop do bot",
        "np" : "Disponibiliza informações da música que está tocando",
        "pause" : "Pausa a música que está tocando",
        "play" : "Toca uma música, ou um índice de música na fila, e conecta o bot a um canal de voz",
        "queue" : "Mostra informações da lista de músicas",
        "remove" : "Remove alguma música da fila",
        "resume" : "Resume a música que estava tocando",
        "seek" : "Vai para um determinado tempo da música",
        "skip" : "Pula um determinado número de músicas na fila",
        "shuffle" : "Embaralha a fila de reprodução",

        "language" : "Define a linguagem do bot para o servidor",

        "ldesc_disconnect" : """Este comando, como o nome sugere, desconecta o bot de algum canal de voz.
Todo registro de músicas do servidor (a fila de reprodução) é excluído na chamada deste comando.""",
        "ldesc_loop" : """Este comando altera o modo de loop do bot. Por padrão, o bot começa no modo sem repetição.
Utilize este comando uma vez para colocá-lo no modo de repetição da fila, mais outra para colocá-lo no modo de repetição do item, e uma última para voltar ao modo sem repetição.""",
        "ldesc_np" : """Este comando mostra informações da música que está tocando. Essas informações são o nome, o tempo atual e a duração da música, e o usuário que a colocou na fila.""",
        "ldesc_pause" : """Este comando pausa a música que está tocando. Para retomar a música, utilize o comando resume""",
        "ldesc_play" : """Este comando é responsável por conectar o bot a um canal de voz (caso ele não esteja) e por colocar algum item na fila.
Como argumento deste comando, você deve infomar:
A url de um vídeo, playlist ou live, do YouTube ou Spotify; 
Um texto de busca que vai adicionar o primeiro vídeo que encontrar com a busca, no YouTube;
Ou o índice de uma música na fila, para tocar imediatamente.""",
        "ldesc_queue" : """Este comando mostra as informações da lista de músicas do servidor.
As informações disponibilizadas são o índice da música na fila, o nome da música, a duração da música e um indicador de tocando agora para a música que está tocando.""",
        "ldesc_remove" : """Este comando remove a música de um índice da fila, que precisa ser especificado. Não confundir com o comando skip, que pula a música atual mas não a remove da fila.""",
        "ldesc_resume" : """Este comando retoma a música que estava tocando. Para ter sucesso, é preciso utilizar este comando depois do comando pause.""",
        "ldesc_seek" : """Este comando vai a um determinado tempo da música que está tocando. 
Por exemplo, se eu quiser ir para o tempo 3 minutos e 2 segundos da música que está tocando, posso utilizar moo seek 03:02, ou moo seek 3:2, ou moo seek 182. Ou seja, é possível passar um argumento como HH:MM:SS, MM:SS ou apenas segundos.""",
        "ldesc_skip" : """Este comando pula um determinado número de músicas na fila. Ele recebe um argumento opcional do número de músicas a serem puladas, mas caso ele não esteja presente, ele pula apenas a música atual.""",
        "ldesc_shuffle" : """Este comando embaralha a fila de reprodução em uma ordem aleatória.""",

        "ldesc_language" : """Este comando define a linguagem para o servidor. 
Ele não recebe argumento algum, mas uma resposta é enviada pelo bot logo após a utilização, mostrando possíveis opções de linguagens.
Como resposta, você deve especificar o índice da linguagem do bot para o servidor. Por padrão, a linguagem do bot é português."""
    },
    'us_en': {
        "desc_mp" : "Audio player of YouTube videos",
        "desc_ss" : "Settings for the server",

        "er_con" : "You need to be connected to a voice channel",
        "er_conb" : "There is no connection with the bot",
        "er_down" : "There was an error with the download of the item",
        "er_index" : "Specify a valid song index",
        "er_ytdl" : "Something went wrong",
        "er_url" : "Something went wrong about the extraction of the information",
        "er_conc" : "There is a conection problem with the channel. Bye bye",
        "er_perm" : "I don't have permission to connect or speak in the channel",
        "er_shoutlen" : "Invalid choice index. The operation is canceled",
        "er_shtimeout" : "30 seconds have passed. The operation is canceled",
        "er_himalformed" : "Something went wrong. Please, verify if the URL is valid",
        "er_hispotifyuri" : "Not yet supported. Only /playlist and /track are supported at the moment",
        "er_hidomain" : "Domain not supported. Only YouTube and Spotify are supported at the moment",
        "song_add" : "Added [{title}]({url}) in position {index} of the queue, by {mention}",
        "song_change" : "It is not the song you were looking for? Type c to change",
        "pl_add" : "Added {pl_len} items, by {mention}",
        "er_nosong" : "There is no song playing",
        "er_skipindex" : "Specify a valid number of songs to skip",
        "er_skiparg" : "Invalid argument",
        "skip_succ" : "Skipped {how_many} song(s)",
        "er_paused" : "The song is already paused",
        "er_nopause" : "There is no song paused",
        "er_seekarg" : "Specify a timestamp in the HOURS:MINUTES:SECONDS format that make sense",
        "er_npdat" : "There was a problem in fetching the time data of the song",
        "np_succnorm" : "Playing {index}. [{title}]({weburl}), by {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Playing {index}. [{title}]({weburl}), by {mention}\nLIVE for {formatted_elapsed} in the server",
        "q_norep" : "No loop",
        "q_qrep" : "Looping: Queue",
        "q_songrep" : "Looping: {song}",
        "q_np" : "(now playing)",
        "q_remaining" : "remaining",
        "q_page"   : """
```markdown
Song queue: <Page {page_plus} of {last_page_plus}>

{songs}

# {in_loop}
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
        "play_duration" : "Duration",
        "play_shcancel" : "Operation canceled",
        "play_by" : "by",
        "play_buildt" : """
```markdown
# Please, choose your song

{songs_str}

[c] : <Cancel>
```
""",
        "inactive_notice" : "For I'm inactive, I'm leaving the vc. Bye bye!",
        "alone_notice" : "I'm alone in the vc for a while. Leaving!",
        "q_next" : "Next song",

        "help_it" : "Categories",
        "help_en" : "Type {help.clean_prefix}{help.invoked_with} <command> for more information about a command.\nAlternatively, {help.clean_prefix}{help.invoked_with} <category> for more information about a category.",

        "disconnect" : "Disconnects bot from a voice channel and closes everything",
        "loop" : "Alters bot's loop mode",
        "np" : "Shows information about the song that is playing",
        "pause" : "Pauses the song that is playing",
        "play" : "Plays a song, or a song index of the queue, and connects the bot to a voice channel",
        "queue" : "Shows informations about the song queue",
        "remove" : "Removes a song from the queue",
        "resume" : "Resumes the song that was playing",
        "seek" : "Seeks a timestamp of the song",
        "skip" : "Skips a number of songs of the queue",
        "shuffle" : "Shuffles the queue",

        "language" : "Defines the language of the bot for the server",

        "ldesc_disconnect" : """This command, as the name suggests, disconnects the bot from a voice channel.
All record of songs in the server (the song queue) is removed on the calling of this command.""",
        "ldesc_loop" : """This command alters the loop mode of the bot. By default, it starts in no loop mode.
Use this command once to set the bot in loop queue mode, again for loop track mode, and a last time to go back to no loop mode.""",
        "ldesc_np" : """This command displays information about the song that is playing. They are the name, the current time and the duration of the song, and the user who inserted it.""",
        "ldesc_pause" : """This command pauses the song that is playing. To resume the song, use the resume command.""",
        "ldesc_play" : """This command is responsible for connecting the bot to a voice channel (if it isn't connected) and for inserting an item to the queue.
As argument of this command, you must provide:
The url of a YouTube, or Spotify, video, playlist or live;
A YouTube search query that will insert the first video of the result.
Or the index of a song in the queue, to play right now.""",
        "ldesc_queue" : """This command displays information about the song queue of the server.
That information is the song index in the queue, the name of the song, the duration of the song, and a now playing indicator for the song that is playing.""",
        "ldesc_remove" : """This command removes the song of an index in the queue, that must be specified. Is not to be mistaken with the skip command, that skips the current song, but doesn't remove it from the queue.""",
        "ldesc_resume" : """This command resumes the song that was playing. To be successful, this command needs to be used after the pause command.""",
        "ldesc_seek" : """This command seeks a timestamp in the song that is playing.
For example, if I'd like to go to 3 minutes and 2 seconds of the song that is playing, I can use moo seek 03:02, or moo seek 3:2, or moo seek 182. It is possible to provide an argument as HH:MM:SS, MM:SS or only seconds.""",
        "ldesc_skip" : """This command skips a number of songs in the queue. It receives an optional argument of the number of songs to be skipped. If it is not specified, it will only skip the current song.""",
        "ldesc_shuffle" : """This command shuffles the queue to a random sequence.""",

        "ldesc_language" : """This command defines the language of the bot for the server. 
It doesn't need any argument, but a response is given by the bot right after, showing possible language options.
As reply, you must specify the index of the language of the bot for the server. By default, the bot's language is Brazillian Portuguese."""

    },
    'es': {
        "desc_mp" : "Reproductor de audio de videos de YouTube",
        "desc_ss" : "Configuración para el servidor",

        "er_con" : "Debe estar conectado a un canal de voz",
        "er_conb" : "No hay conexión con el bot",
        "er_down" : "Hubo un error al descargar un elemento",
        "er_index" : "Especifica un índice de música válido",
        "er_ytdl" : "Algo salió mal",
        "er_url" : "Algo salió mal al extraer información",
        "er_conc" : "Hay un problema de conexión con el canal. Adiooos",
        "er_perm" : "No tengo permiso para iniciar sesión o hablar en el canal",
        "er_shoutlen" : "Índice de elección no válido. Se cancela la operación",
        "er_shtimeout" : "Han pasado 30 segundos. Se cancela la operación",
        "er_himalformed" : "Algo salió mal. Verifique que la URL sea válida ",
        "er_hispotifyuri" : "Aún no es compatible. Actualmente solo se admiten /playlist o /track",
        "er_hidomain" : "Dominio no compatible. Actualmente solo se admiten YouTube y Spotify",
        "song_add" : "Agregó [{title}]({url}) en la posición {index} de la cola, por {mention}",
        "song_change" : "No era la canción que buscabas? Escriba c para cambiar",
        "pl_add" : "Agregó {pl_len} elementos, por {mention}",
        "er_nosong" : "No hay música sonando",
        "er_skipindex" : "Especifique un número válido de musicas para saltar",
        "er_skiparg" : "Argumento no válido",
        "skip_succ" : "Salteado {how_many} música(s)",
        "er_paused" : "La música ya esta pausada",
        "er_nopause" : "No hay música pausada",
        "er_seekarg" : "Proporcione una marca de tiempo en el formato HORAS: SEGUNDOS: MINUTOS que tenga sentido",
        "er_npdat" : "Hubo un problema al obtener los datos de tempo de la música",
        "np_succnorm" : "Tocando {index}. [{title}]({weburl}), por {mention}\n{progress_bar} {formatted_elapsed} / {formatted_duration}",
        "np_succlive" : "Tocando {index}. [{title}]({weburl}), por {mention}\nLIVE durante {formatted_elapsed} en el servidor",
        "q_norep" : "Sin repetición",
        "q_qrep" : "Repetición: Cola",
        "q_songrep" : "Repetición: {song}",
        "q_np" : "(tocando ahora)",
        "q_remaining" : "restante",
        "q_page"   : """
```markdown
Cola de reproducción: <Pagina {page_plus} de {last_page_plus}>

{songs}

# {in_loop}
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
        "play_duration" : "Duración",
        "play_shcancel" : "Operación cancelada",
        "play_by" : "por",
        "play_buildt" : """
```markdown
# Por favor, haga su elección de música  

{songs_str}

[c] : <Cancelar>
```
""",
        "inactive_notice" : "Porque estoy inactivo, me voy a salir del voice. ¡Adioooos!",
        "alone_notice" : "Estoy solo en el voice por un tiempo. ¡Dejando!",
        "q_next" : "Siguiente música",

        "help_it" : "Categorías",
        "help_en" : "Escribe {help.clean_prefix}{help.invoked_with} <comando> para obtener más información sobre un comando.\nAlternativamente, {help.clean_prefix}{help.invoked_with} <categoría> para más información sobre una categoría.",

        "disconnect" : "Desconecta el bot del voice y cierra tudo",
        "loop" : "Cambia el modo de repetición del bot ",
        "np" : "Proporciona información sobre la música que se está reproduciendo actualmente",
        "pause" : "Pausa la música que está tocando",
        "play" : "Reproduce una música, o un índice de música en la cola, y conecta el bot a un canal de voz",
        "queue" : "Muestra información de la lista de música",
        "remove" : "Quita una música de la cola",
        "resume" : "Resume la música que estaba tocando",
        "seek" : "Va a un momento determinado de la música",
        "skip" : "Se salta una cierta cantidad de músicas en la cola",
        "shuffle" : "Genera una orden aleatoria de la cola",

        "language" : "Define el idioma del bot para el servidor",

        "ldesc_disconnect" : """Este comando, como su nombre indica, desconecta al bot de algún canal de voz.
Todos los registros de música del servidor (la cola de reproducción) se eliminan al llamar a este comando.""",
        "ldesc_loop" : """Este comando cambia el modo de bucle del bot. De forma predeterminada, el bot se inicia en modo de no repetición.
Utilice este comando una vez para ponerlo en modo de repetición en cola, una vez más para ponerlo en modo de repetición de elementos y un último par para volver al modo sin repetición.""",
        "ldesc_np" : """Este comando muestra información de la canción que se está reproduciendo actualmente. Esta información es el nombre, el tempo actual y la duración de la canción, y el usuario que la puso en cola. """,
        "ldesc_pause" : """Este comando detiene la canción que se está reproduciendo actualmente. Para reanudar la música, use el comando resume""",
        "ldesc_play" : """Este comando se encarga de conectar el bot a un canal de voz (si no está conectado) y de poner algún elemento en la cola.
Como argumento de este comando, debe ingresar:
La URL de un video, lista de reproducción o en vivo de YouTube o Spotify;
Un texto de búsqueda que agregará el primer video que encuentre con la búsqueda, en YouTube;
O el índice de una canción en la cola, para reproducir de inmediato.""",
        "ldesc_queue" : """Este comando mostra as informações da lista de músicas do servidor.
As informações disponibilizadas são o índice da música na fila, o nome da música, a duração da música e um indicador de tocando agora para a música que está tocando.""",
        "ldesc_remove" : """Este comando muestra la información de la lista de reproducción del servidor.
La información proporcionada es el índice de la canción en la cola, el nombre de la canción, la duración de la canción y un indicador de reproducción actual para la canción que se está reproduciendo actualmente. """,
        "ldesc_resume" : """Este comando reanuda la canción que se estaba reproduciendo. Para tener éxito, debe utilizar este comando después del comando de pause.""",
        "ldesc_seek" : """Este comando va a un cierto tempo de la canción que se está reproduciendo actualmente.
Por ejemplo, si quiero ir al tiempo de 3 minutos y 2 segundos de la canción que se está reproduciendo actualmente, puedo usar moo seek 3:02, moo seek 3:2, o moo seek 182. Es decir, es posible pasar un argumento como HH:MM:SS, MM:SS, o solo segundos.""",
        "ldesc_skip" : """Este comando salta una cierta cantidad de canciones en la cola. Se necesita un argumento opcional del número de canciones que se van a saltar, pero si no está presente, simplemente se salta la canción actual.""",
        "ldesc_shuffle" : """Este comando baraja la cola en una orden aleatoria.""",

        "ldesc_language" : """Este comando establece el idioma del servidor.
No requiere ningún argumento, pero el bot envía una respuesta inmediatamente después de su uso, mostrando posibles opciones de idioma.
En respuesta, debe especificar el índice de idioma del bot para el servidor. De forma predeterminada, el idioma del bot es el portugués."""

    }
}
