Ho inserito dentro all'oggetto _Finger_ come trovarlo ma, ciò implica che qualsiasi cosa verrà selezionata allora sarà soggetta ad ogni tipo di trasformazione
Tutto ciò si nota nel metodo *make_locators_attributes* che, automaticamente non riesce ad individuare la catena *_rig* ma, nel caso venga selezionata, il processo richiesto va a buon fine.
A questo punto, sconsiglio di definire la catena madre dentro la classe *Finger* una volta per tutte

Funziona tutto abbastanza bene se si seleziona manualmente la catena, ciò significa che l'utilizzo deve essere troppo consapevole e, al contempo, mostra il fianco ad un utilizzo degli oggetti decisamente poco efficace