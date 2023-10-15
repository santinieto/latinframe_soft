# Consulta SQL
query = 'SELECT CHANNEL_ID FROM CHANNEL'
# query = 'UPDATE CHANNEL_ID FROM CHANNEL'

# Obtener la primer palabra
fw = query.split()[0].lower()
print(fw)

# Opero
if fw == 'select':
    print('Executing SELECT')

else:
    print('Executing SQL')