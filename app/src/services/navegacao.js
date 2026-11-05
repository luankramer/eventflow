// Volta para a tela anterior; se não houver histórico (ex.: app aberto direto nessa tela),
// vai para a rota indicada.
export function voltarPara(ionRouter, rotaPadrao) {
  if (ionRouter.canGoBack()) ionRouter.back()
  else ionRouter.navigate(rotaPadrao, 'back', 'replace')
}
