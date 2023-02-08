from data_scrapper import get_jobs

df = get_jobs("data scientist intern", 10)
df.to_excel('output.xlsx')
