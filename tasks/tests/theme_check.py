from invoke import task


@task
def theme_check(context):
    """Run Shopify Theme Check"""
    print("\n------------")
    print("Shopify Theme Check")
    print("------------\n")
    context.run("shopify theme check")
