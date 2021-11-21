

from pytdx.reader import TdxDailyBarReader, TdxFileNotFoundException


file = r'C:\new_jyplug\vipdoc\sh\lday\sh688001.day'

reader = TdxDailyBarReader()

df = reader.get_df_by_file(file)

print(df)